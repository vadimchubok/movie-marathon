from django.urls import path
from .views import (
    MarathonListView,
    MarathonCreateView,
    MarathonDetailView,
    MarathonUpdateView,
    MarathonDeleteView,
    MarathonMovieSearchView,
    JoinMarathonView
)

app_name = "marathons"

urlpatterns = [
    path("", MarathonListView.as_view(), name="list"),
    path("create/", MarathonCreateView.as_view(), name="create"),
    path("<int:pk>/", MarathonDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", MarathonUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", MarathonDeleteView.as_view(), name="delete"),
    path("<int:marathon_id>/join/", JoinMarathonView.as_view(), name="join"),
    path("search_movies/", MarathonMovieSearchView.as_view(), name="search_movies"),
]
