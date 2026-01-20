from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User

    list_display = (
        "username",
        "email",
        "role",
        "status",
        "is_staff",
        "is_active",
    )

    list_filter = (
        "role",
        "status",
        "is_staff",
        "is_active",
    )

    search_fields = (
        "username",
        "email",
    )

    ordering = ("username",)

    fieldsets = (
        (None, {
            "fields": ("username", "password")
        }),
        ("Personal info", {
            "fields": ("first_name", "last_name", "email")
        }),
        ("Custom fields", {
            "fields": ("role", "status")
        }),
        ("Permissions", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        ("Important dates", {
            "fields": ("last_login", "date_joined")
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "username",
                "email",
                "password1",
                "password2",
                "role",
                "status",
                "is_staff",
                "is_superuser",
            ),
        }),
    )

    filter_horizontal = (
        "groups",
        "user_permissions",
    )
