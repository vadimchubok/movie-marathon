from cloudinary.models import CloudinaryField
from django.conf import settings
from django.db import models


class Genre(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self: "Genre") -> str:
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=200)
    year = models.IntegerField()
    genre = models.ManyToManyField(
        Genre,
        blank=True,
        related_name="movies",
    )
    poster = CloudinaryField("image", blank=True, null=True)
    imdb_rating = models.FloatField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    @property
    def poster_url(self):
        if self.poster and hasattr(self.poster, 'url'):
            return str(self.poster.url)
        return ""

    class Meta:
        ordering = ["-title"]

    def __str__(self: "Movie") -> str:
        return self.title


class UserRating(models.Model):
    value = models.PositiveSmallIntegerField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ratings",
    )
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name="ratings",
    )


class Review(models.Model):
    text = models.TextField()
    is_review = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self: "Review") -> str:
        return f"{self.author} – {self.movie}"
