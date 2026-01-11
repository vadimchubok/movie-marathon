from django.test import TestCase
from django.contrib.auth import get_user_model

from movies.models import (
    Movie,
    Genre,
    UserRating,
    Review
)

User = get_user_model()


class GenreModelTest(TestCase):
    def test_genre_str(self):
        genre = Genre.objects.create(name="Drama")
        self.assertEqual(str(genre), "Drama")


class MovieModelTest(TestCase):
    def setUp(self):
        self.genre = Genre.objects.create(name="Action")

        self.movie = Movie.objects.create(
            title="Test Movie",
            year=2024,
            imdb_rating=8.5,
            description="Test description",
        )
        self.movie.genre.add(self.genre)

    def test_movie_created(self):
        self.assertEqual(Movie.objects.count(), 1)

    def test_movie_str(self):
        self.assertEqual(str(self.movie), "Test Movie")

    def test_movie_year(self):
        self.assertEqual(self.movie.year, 2024)

    def test_movie_genre_relation(self):
        self.assertIn(self.genre, self.movie.genre.all())

    def test_movie_poster_url_empty(self):
        self.assertEqual(self.movie.poster_url, "")


class UserRatingModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="rating_user",
            password="12345"
        )

        self.movie = Movie.objects.create(
            title="Rated Movie",
            year=2023
        )

        self.rating = UserRating.objects.create(
            value=8,
            author=self.user,
            movie=self.movie
        )

    def test_rating_created(self):
        self.assertEqual(UserRating.objects.count(), 1)

    def test_rating_author(self):
        self.assertEqual(self.rating.author, self.user)

    def test_rating_movie(self):
        self.assertEqual(self.rating.movie, self.movie)

    def test_rating_value(self):
        self.assertEqual(self.rating.value, 8)


class ReviewModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="review_user",
            password="12345"
        )

        self.movie = Movie.objects.create(
            title="Reviewed Movie",
            year=2022
        )

        self.review = Review.objects.create(
            text="Great movie!",
            is_review=True,
            author=self.user,
            movie=self.movie
        )

    def test_review_created(self):
        self.assertEqual(Review.objects.count(), 1)

    def test_review_str(self):
        expected = f"{self.user} – {self.movie}"
        self.assertEqual(str(self.review), expected)

    def test_review_author(self):
        self.assertEqual(self.review.author, self.user)

    def test_review_movie(self):
        self.assertEqual(self.review.movie, self.movie)

    def test_review_ordering(self):
        reviews = Review.objects.all()
        self.assertEqual(reviews[0], self.review)
