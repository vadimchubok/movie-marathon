from django.utils import timezone
from django.conf import settings
from django.db import models

from movies.models import Movie


class Marathon(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField(default=timezone.now)
    total_duration = models.IntegerField(default=0)

    curator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="curated_marathons",
    )

    movies = models.ManyToManyField(Movie, blank=True)

    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="participated_marathons",
        blank=True,
    )

    def __str__(self):
        return self.title


class MarathonTicket(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="marathon_tickets",
    )
    marathon = models.ForeignKey(
        Marathon,
        on_delete=models.CASCADE,
        related_name="tickets",
    )

    def __str__(self):
        return f"{self.user} → {self.marathon}"
