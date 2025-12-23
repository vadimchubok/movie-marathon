from django.urls import path
from .views import (
    MarathonListView,
    MarathonCreateView,
    MarathonDetailView,
    MarathonUpdateView,
    MarathonDeleteView,
    join_marathon,
    marathon_movie_search,
)

app_name = "marathons"

urlpatterns = [
    path("", MarathonListView.as_view(), name="list"),
    path("create/", MarathonCreateView.as_view(), name="create"),
    path("<int:pk>/", MarathonDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", MarathonUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", MarathonDeleteView.as_view(), name="delete"),
    path("<int:marathon_id>/join/", join_marathon, name="join"),
    path("search_movies/", marathon_movie_search, name="search_movies"),
]
