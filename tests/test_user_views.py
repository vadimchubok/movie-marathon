from django.test import TestCase
from django.urls import reverse

from users.models import User


class RegisterViewTests(TestCase):
    def setUp(self):
        self.url = reverse("users:register")
        self.user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "strongpassword123",
            "password2": "strongpassword123",
        }

    def test_register_view_get_status(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/register.html")

    def test_register_view_post_creates_user(self):
        response = self.client.post(self.url, self.user_data)
        login_url = reverse("login")
        self.assertRedirects(response, login_url)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_view_post_invalid_data(self):
        invalid_data = self.user_data.copy()
        invalid_data["password2"] = "mismatch"
        response = self.client.post(self.url, invalid_data)
        self.assertEqual(response.status_code, 200)
        form = response.context.get("form")
        self.assertIsNotNone(form)
        self.assertTrue(form.errors)
        self.assertIn("password2", form.errors)
        self.assertFalse(User.objects.filter(username="newuser").exists())
