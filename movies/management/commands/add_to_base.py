import csv
import ast
import uuid
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

import cloudinary.uploader
from cloudinary.utils import cloudinary_url

from movies.models import Movie, Genre

BASE_DIR = Path(settings.BASE_DIR)
CSV_PATH = BASE_DIR / "films_translated.csv"  # твій CSV
IMAGES_DIR = BASE_DIR / "films"          # папка з постерами


def clean_year(value):
    try:
        year = int(float(str(value).strip()))
        if 1800 <= year <= 2100:
            return year
    except Exception:
        pass
    return None


class Command(BaseCommand):
    help = "Import movies and genres from CSV (images + genres) with CloudinaryField"

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

                movie = Movie.objects.create(
                    title=title,
                    year=year,
                    description=row.get("description") or "",
                    imdb_rating=rating,
                )
                self.stdout.write(f"✅ Movie created: {title}")

                # ===== POSTER =====
                image_name = row.get("image")
                image_path = IMAGES_DIR / image_name if image_name else None
                if image_path and image_path.exists():
                    ext = image_path.suffix.lower()
                    unique_name = f"{uuid.uuid4()}{ext}"  # унікальне ім'я

                    upload_result = cloudinary.uploader.upload(
                        str(image_path),
                        folder="movies"
                    )

                    movie.poster = upload_result["public_id"]
                    movie.save()

                    # Правильний URL
                    url, options = cloudinary_url(movie.poster)
                    self.stdout.write(f"🖼 Poster uploaded: {url}")

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
