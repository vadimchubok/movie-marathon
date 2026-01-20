from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from movies.models import (
    Movie,
    Genre,
    UserRating,
    Review
)

User = get_user_model()


class MovieViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            password="password"
        )
        self.genre1 = Genre.objects.create(name="Action")
        self.genre2 = Genre.objects.create(name="Comedy")
        self.movie1 = Movie.objects.create(title="Movie One", year=2020)
        self.movie1.genre.add(self.genre1)
        self.movie2 = Movie.objects.create(title="Movie Two", year=2021)
        self.movie2.genre.add(self.genre2)

    def test_movie_list_view_status_and_context(self):
        url = reverse("movies:movie_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("movies_list", response.context)
        self.assertIn(self.movie1, response.context["movies_list"])
        self.assertIn(self.movie2, response.context["movies_list"])
        self.assertIn("genres", response.context)
        self.assertIn(self.genre1, response.context["genres"])
        self.assertIn(self.genre2, response.context["genres"])

    def test_movie_list_view_search_and_filter(self):
        url = reverse("movies:movie_list")
        response = self.client.get(url, {"q": "Movie One"})
        self.assertQuerySetEqual(
            response.context["movies_list"],
            [repr(self.movie1)],
            transform=repr
        )
        response = self.client.get(url, {"genre": [self.genre2.id]})
        self.assertQuerySetEqual(
            response.context["movies_list"],
            [repr(self.movie2)],
            transform=repr
        )
        response = self.client.get(url, {"year": 2020})
        self.assertQuerySetEqual(
            response.context["movies_list"],
            [repr(self.movie1)],
            transform=repr
        )

    def test_movie_list_view_sorting(self):
        url = reverse("movies:movie_list")
        response = self.client.get(url, {"sort": "title"})
        movies_sorted = list(response.context["movies_list"])
        expected_sorted = sorted([self.movie1, self.movie2], key=lambda m: m.title)
        self.assertEqual(movies_sorted, expected_sorted)
        response = self.client.get(url, {"sort": "year"})
        movies_sorted = list(response.context["movies_list"])
        expected_sorted = sorted(
            [self.movie1, self.movie2],
            key=lambda m: m.year,
            reverse=True
        )
        self.assertEqual(movies_sorted, expected_sorted)

    def test_movie_detail_view_get(self):
        url = reverse("movies:movie_detail", args=[self.movie1.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["object"], self.movie1)

    def test_movie_detail_view_post_authenticated_rating_and_review(self):
        self.client.login(username="testuser", password="password")
        url = reverse("movies:movie_detail", args=[self.movie1.pk])
        response = self.client.post(
            url,
            {"rating": 9, "text": "Amazing!", "is_review": "on"}
        )
        self.assertRedirects(response, url)
        self.assertTrue(
            UserRating.objects.filter(
                author=self.user,
                movie=self.movie1,
                value=9
            ).exists()
        )
        self.assertTrue(
            Review.objects.filter(
                author=self.user,
                movie=self.movie1,
                text="Amazing!",
                is_review=True
            ).exists()
        )

    def test_movie_search_view(self):
        url = reverse("movies:movie_search")
        response = self.client.get(url, {"q": "Movie"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
        response = self.client.get(url, {"q": "X"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])
