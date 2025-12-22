from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserModelTest(TestCase):
    def test_user_creation_with_defaults(self):
        user = User.objects.create_user(
            username="testuser",
            password="12345"
        )

        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.role, User.Role.USER)
        self.assertEqual(user.status, User.Status.REGULAR)
        self.assertTrue(user.check_password("12345"))

    def test_user_str(self):
        user = User.objects.create_user(
            username="vadim",
            password="12345"
        )

        self.assertEqual(str(user), "vadim")

    def test_user_with_custom_role_and_status(self):
        user = User.objects.create_user(
            username="curator",
            password="12345",
            role=User.Role.CURATOR,
            status=User.Status.REVIEWER,
        )

        self.assertEqual(user.role, User.Role.CURATOR)
        self.assertEqual(user.status, User.Status.REVIEWER)

    def test_user_roles_choices(self):
        self.assertIn(User.Role.USER, User.Role.values)
        self.assertIn(User.Role.CURATOR, User.Role.values)

    def test_user_status_choices(self):
        self.assertIn(User.Status.REGULAR, User.Status.values)
        self.assertIn(User.Status.REVIEWER, User.Status.values)
