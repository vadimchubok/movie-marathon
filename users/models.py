from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        USER = "USER", "user"
        CURATOR = "CURATOR", "curator"

    class Status(models.TextChoices):
        REGULAR = "REGULAR", "regular"
        REVIEWER = "REVIEWER", "reviewer"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.REGULAR,
    )

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_users",
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_users_permissions",
        blank=True,
    )

    def __str__(self):
        return self.username
