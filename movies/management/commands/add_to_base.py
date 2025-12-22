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
    parts = path.split('/')
    try:
        idx = parts.index('movies')
        filename = parts[idx + 1]
        public_id = f"movies/{filename.rsplit('.', 1)[0]}"
        return public_id
    except ValueError:
        return ""
    except IndexError:
        return ""

class Command(BaseCommand):
    help = "Import movies from CSV with Cloudinary URL and save correct public_id"

    def handle(self, *args, **options):
        self.stdout.write("🧹 Clearing existing Movies and Genres...")
        Movie.objects.all().delete()
        Genre.objects.all().delete()

        self.stdout.write("📄 Loading CSV...")

        with open(CSV_PATH, encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row_num, row in enumerate(reader, start=1):
                title = row.get("title", "").strip()
                if not title:
                    self.stdout.write(f"⚠️ Empty title, skipping row {row_num}")
                    continue

                year = clean_year(row.get("year"))
                if not year:
                    self.stdout.write(f"⚠️ Invalid year for {title}, skipping")
                    continue

                rating = None
                if row.get("rating"):
                    try:
                        rating = float(row["rating"])
                    except ValueError:
                        rating = None

                image_url = row.get("image", "").strip()
                public_id = url_to_public_id(image_url)

                movie = Movie.objects.create(
                    title=title,
                    year=year,
                    description=row.get("description") or "",
                    imdb_rating=rating,
                    poster=public_id
                )
                self.stdout.write(f"✅ Movie created: {title} (poster: {public_id})")

                # ===== GENRES =====
                genres = []
                if row.get("genres"):
                    try:
                        genres = ast.literal_eval(row["genres"])
                        if not isinstance(genres, list):
                            genres = []
                    except Exception:
                        self.stdout.write("⚠️ Invalid genres format, skipping genres")

                for genre_name in genres:
                    genre_name = str(genre_name).strip()
                    if not genre_name:
                        continue
                    genre, _ = Genre.objects.get_or_create(name=genre_name)
                    movie.genre.add(genre)
                    self.stdout.write(f"🎭 Genre added: {genre.name}")

                movie.save()

        self.stdout.write("\n🎉 IMPORT COMPLETED")
