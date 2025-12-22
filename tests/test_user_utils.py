from django.test import TestCase
from django.contrib.auth import get_user_model

from movies.models import Movie, Review
from users.utils import update_user_status

User = get_user_model()


class UpdateUserStatusTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="password"
        )
        self.movie = Movie.objects.create(title="Test Movie", year=2023)

    def test_user_role_and_status_update_with_10_reviews(self):
        for i in range(10):
            Review.objects.create(
                author=self.user,
                movie=self.movie,
                text=f"Review {i}",
                is_review=True
            )

        update_user_status(self.user)

        self.user.refresh_from_db()
        self.assertEqual(self.user.role, self.user.Role.CURATOR)
        self.assertEqual(self.user.status, self.user.Status.REVIEWER)

    def test_user_role_and_status_not_update_with_less_than_10_reviews(self):
        for i in range(5):
            Review.objects.create(
                author=self.user,
                movie=self.movie,
                text=f"Review {i}",
                is_review=True
            )

        update_user_status(self.user)

        self.user.refresh_from_db()
        self.assertNotEqual(self.user.role, self.user.Role.CURATOR)
        self.assertNotEqual(self.user.status, self.user.Status.REVIEWER)
