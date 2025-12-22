from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from marathons.models import Marathon, MarathonTicket
from movies.models import Movie


User = get_user_model()


class MarathonBaseTestCase(TestCase):
    def setUp(self):
        self.curator = User.objects.create_user(
            username="curator",
            password="1234",
            role=User.Role.CURATOR,
        )

        self.user = User.objects.create_user(
            username="user",
            password="1234",
            role=User.Role.USER,
        )

        self.movie = Movie.objects.create(
            title="Test movie",
            year=2024,
        )

        self.marathon = Marathon.objects.create(
            title="Test marathon",
            curator=self.curator,
            start_date=timezone.now().date(),
            total_duration=120,
        )
        self.marathon.movies.add(self.movie)

    def valid_marathon_data(self, **overrides):
        data = {
            "title": "New marathon",
            "start_date": timezone.now().isoformat(),
            "total_duration": 150,
            "movies": [self.movie.id],
        }
        data.update(overrides)
        return data


class MarathonListViewTest(MarathonBaseTestCase):

    def test_login_required(self):
        response = self.client.get(reverse("marathons:list"))
        self.assertEqual(response.status_code, 302)

    def test_list_view(self):
        self.client.login(username="user", password="1234")
        response = self.client.get(reverse("marathons:list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.marathon.title)


class MarathonCreateViewTest(MarathonBaseTestCase):

    def test_only_curator_can_create(self):
        self.client.login(username="user", password="1234")
        response = self.client.get(reverse("marathons:create"))
        self.assertEqual(response.status_code, 403)

    def test_curator_can_create_marathon(self):
        self.client.login(username="curator", password="1234")

        response = self.client.post(
            reverse("marathons:create"),
            data=self.valid_marathon_data(title="Created marathon"),
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Marathon.objects.filter(title="Created marathon").exists()
        )


class MarathonDetailViewTest(MarathonBaseTestCase):

    def test_detail_view(self):
        self.client.login(username="user", password="1234")

        response = self.client.get(
            reverse("marathons:detail", args=[self.marathon.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["marathon"], self.marathon)
        self.assertFalse(response.context["is_joined"])


class MarathonUpdateViewTest(MarathonBaseTestCase):

    def test_only_curator_can_edit(self):
        self.client.login(username="user", password="1234")

        response = self.client.get(
            reverse("marathons:edit", args=[self.marathon.id])
        )

        self.assertEqual(response.status_code, 403)

    def test_curator_can_edit(self):
        self.client.login(username="curator", password="1234")

        response = self.client.post(
            reverse("marathons:edit", args=[self.marathon.id]),
            data=self.valid_marathon_data(title="Updated title"),
        )

        self.assertEqual(response.status_code, 302)

        self.marathon.refresh_from_db()
        self.assertEqual(self.marathon.title, "Updated title")


class MarathonDeleteViewTest(MarathonBaseTestCase):

    def test_only_curator_can_delete(self):
        self.client.login(username="user", password="1234")

        response = self.client.post(
            reverse("marathons:delete", args=[self.marathon.id])
        )

        self.assertEqual(response.status_code, 403)

    def test_curator_can_delete(self):
        self.client.login(username="curator", password="1234")

        response = self.client.post(
            reverse("marathons:delete", args=[self.marathon.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            Marathon.objects.filter(id=self.marathon.id).exists()
        )


class JoinMarathonTest(MarathonBaseTestCase):

    def test_join_marathon(self):
        self.client.login(username="user", password="1234")

        response = self.client.post(
            reverse("marathons:join", args=[self.marathon.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            self.marathon.participants.filter(id=self.user.id).exists()
        )
        self.assertTrue(
            MarathonTicket.objects.filter(
                user=self.user,
                marathon=self.marathon,
            ).exists()
        )
