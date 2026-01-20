from django.urls import path

from movies.views import (
    MovieListView,
    MovieDetailView,
    MovieSearchView,
    ReviewDeleteView
)

urlpatterns = [
    path("", MovieListView.as_view(), name="movie_list"),
    path("<int:pk>/", MovieDetailView.as_view(), name="movie_detail"),
    path("search/", MovieSearchView.as_view(), name="movie_search"),
    path("review/<int:pk>/delete/", ReviewDeleteView.as_view(), name="review_delete"),

]

app_name = "movies"
