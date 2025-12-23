import csv
import ast
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from movies.models import Movie, Genre

BASE_DIR = Path(settings.BASE_DIR)
CSV_PATH = BASE_DIR / "films.csv"


def clean_year(value):
    try:
        year = int(float(str(value).strip()))
        if 1800 <= year <= 2100:
            return year
    except Exception:
        pass
    return None


def url_to_public_id(url: str) -> str:
    if not url:
        return ""
    import urllib.parse
    path = urllib.parse.urlparse(url).path
    parts = path.split("/")
    try:
        idx = parts.index("movies")
        filename = parts[idx + 1]
        return f"movies/{filename.rsplit('.', 1)[0]}"
    except (ValueError, IndexError):
        return ""


class Command(BaseCommand):
    help = "Import movies from CSV safely (no duplicate M2M, no title collisions)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete existing movies and genres before import",
        )

    def handle(self, *args, **options):
        if options["flush"]:
            self.stdout.write("🧹 Clearing existing Movies and Genres...")
            Movie.objects.all().delete()
            Genre.objects.all().delete()

        self.stdout.write("📄 Loading CSV...")

        movies_data = []
        genres_set = set()
        skipped = 0

        with open(CSV_PATH, encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row_num, row in enumerate(reader, start=1):
                title = (row.get("title") or "").strip()
                year = clean_year(row.get("year"))

                if not title or not year:
                    skipped += 1
                    continue

                rating = None
                if row.get("rating"):
                    try:
                        rating = float(row["rating"])
                    except ValueError:
                        pass

                image_url = (row.get("image") or "").strip()
                public_id = url_to_public_id(image_url)

                genres = []
                if row.get("genres"):
                    try:
                        genres = ast.literal_eval(row["genres"])
                    except Exception:
                        genres = []

                # 🔑 унікальні, очищені жанри
                genres = list({str(g).strip() for g in genres if str(g).strip()})
                genres_set.update(genres)

                movies_data.append({
                    "title": title,
                    "year": year,
                    "description": row.get("description") or "",
                    "imdb_rating": rating,
                    "poster": public_id,
                    "genres": genres,
                })

        # ===== CREATE GENRES =====
        self.stdout.write(f"🎭 Creating {len(genres_set)} genres...")
        Genre.objects.bulk_create(
            [Genre(name=name) for name in genres_set],
            ignore_conflicts=True,
        )

        genres_by_name = {
            genre.name: genre for genre in Genre.objects.all()
        }

        # ===== CREATE MOVIES =====
        self.stdout.write(f"🎬 Creating {len(movies_data)} movies...")
        movie_objs = [
            Movie(
                title=data["title"],
                year=data["year"],
                description=data["description"],
                imdb_rating=data["imdb_rating"],
                poster=data["poster"],
            )
            for data in movies_data
        ]

        Movie.objects.bulk_create(movie_objs)

        # ===== LINK M2M SAFELY =====
        self.stdout.write("🔗 Linking movies with genres...")
        through_model = Movie.genre.through
        m2m_links = []

        movies = list(Movie.objects.all())

        for movie, data in zip(movies, movies_data):
            for genre_name in data["genres"]:
                genre = genres_by_name.get(genre_name)
                if genre:
                    m2m_links.append(
                        through_model(
                            movie_id=movie.id,
                            genre_id=genre.id
                        )
                    )

        through_model.objects.bulk_create(
            m2m_links,
            ignore_conflicts=True,
        )

        # ===== SUMMARY =====
        self.stdout.write("")
        self.stdout.write("✅ IMPORT FINISHED")
        self.stdout.write(f"🎬 Movies in DB: {Movie.objects.count()}")
        self.stdout.write(f"🎭 Genres in DB: {Genre.objects.count()}")
        self.stdout.write(f"⛔ Skipped CSV rows: {skipped}")
        self.stdout.write("🚀 Ready to use")
