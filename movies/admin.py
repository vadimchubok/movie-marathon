from django.contrib import admin
from django.utils.html import format_html

from .models import Movie, Genre, Review, UserRating


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ("author", "created_at")
    fields = ("author", "text", "is_review", "created_at")
    show_change_link = True


class RatingInline(admin.TabularInline):
    model = UserRating
    extra = 0
    readonly_fields = ("author",)
    fields = ("author", "value")


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "year",
        "imdb_rating",
        "genres_list",
        "poster_preview",
    )

    list_filter = (
        "year",
        "genre",
    )

    search_fields = (
        "title",
        "description",
    )

    filter_horizontal = (
        "genre",
    )

    inlines = (
        ReviewInline,
        RatingInline,
    )

    def genres_list(self, obj):
        return ", ".join(g.name for g in obj.genre.all())
    genres_list.short_description = "Genres"

    def poster_preview(self, obj):
        if obj.poster and hasattr(obj.poster, "url"):
            return format_html(
                '<img src="{}" style="height:80px;border-radius:6px;" />',
                obj.poster.url
            )
        return "—"
    poster_preview.short_description = "Poster"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "author",
        "movie",
        "is_review",
        "created_at",
    )

    list_filter = (
        "is_review",
        "created_at",
    )

    search_fields = (
        "author__username",
        "movie__title",
        "text",
    )


@admin.register(UserRating)
class UserRatingAdmin(admin.ModelAdmin):
    list_display = (
        "author",
        "movie",
        "value",
    )

    list_filter = (
        "value",
    )

    search_fields = (
        "author__username",
        "movie__title",
    )
