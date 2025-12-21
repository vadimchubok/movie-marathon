from django.urls import path

from movies.views import MovieListView, MovieDetailView, movie_search

urlpatterns = [
    path("", MovieListView.as_view(), name="movie_list"),
    path("<int:pk>/", MovieDetailView.as_view(), name="movie_detail"),
    path("search/", movie_search, name="movie_search"),

]

app_name = "movies"