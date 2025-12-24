from django.contrib import admin

from .models import Marathon, MarathonTicket


@admin.register(Marathon)
class MarathonAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "curator",
        "start_date",
        "total_duration",
        "movies_count",
        "participants_count",
    )

    list_filter = (
        "start_date",
        "curator",
    )

    search_fields = (
        "title",
        "description",
        "curator__username",
    )

    filter_horizontal = (
        "movies",
        "participants",
    )

    readonly_fields = (
        "total_duration",
    )

    fieldsets = (
        (None, {
            "fields": (
                "title",
                "description",
                "curator",
            )
        }),
        ("Schedule", {
            "fields": (
                "start_date",
                "total_duration",
            )
        }),
        ("Content", {
            "fields": (
                "movies",
            )
        }),
        ("Participants", {
            "fields": (
                "participants",
            )
        }),
    )

    def movies_count(self, obj):
        return obj.movies.count()
    movies_count.short_description = "Movies"

    def participants_count(self, obj):
        return obj.participants.count()
    participants_count.short_description = "Participants"


@admin.register(MarathonTicket)
class MarathonTicketAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "marathon",
    )

    list_filter = (
        "marathon",
    )

    search_fields = (
        "user__username",
        "marathon__title",
    )
