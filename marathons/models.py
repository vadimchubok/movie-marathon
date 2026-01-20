from django.conf import settings
from django.db import models

from movies.models import Movie


class Marathon(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField()
    total_duration = models.PositiveIntegerField(
        help_text="Total duration in minutes"
    )

    curator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="curated_marathons",
    )

    movies = models.ManyToManyField(Movie)

    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="participated_marathons",
        blank=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["title", "start_date"],
                name="unique_marathon_title_start_date",
            )
        ]

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
