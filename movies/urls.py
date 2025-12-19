from django.urls import path

from movies.views import MovieListView, MovieDetailView

urlpatterns = [
    path("", MovieListView.as_view(), name="movie_list"),
    path("<int:pk>/", MovieDetailView.as_view(), name="movie_detail"),

]

app_name = "movies"