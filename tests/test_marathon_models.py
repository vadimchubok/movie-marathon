from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from movies.models import Movie
from marathons.models import (
    Marathon,
    MarathonTicket
)

User = get_user_model()


class MarathonModelTest(TestCase):
    def setUp(self):
        self.curator = User.objects.create_user(
            username="curator",
            password="12345"
        )

        self.participant = User.objects.create_user(
            username="participant",
            password="12345"
        )

        self.movie = Movie.objects.create(
            title="Test Movie",
            year=2024
        )

        self.marathon = Marathon.objects.create(
            title="Test Marathon",
            description="Some description",
            start_date=timezone.now(),
            total_duration=120,
            curator=self.curator
        )

        self.marathon.movies.add(self.movie)
        self.marathon.participants.add(self.participant)

    def test_marathon_created(self):
        self.assertEqual(Marathon.objects.count(), 1)

    def test_marathon_str(self):
        self.assertEqual(str(self.marathon), "Test Marathon")

    def test_marathon_curator(self):
        self.assertEqual(self.marathon.curator, self.curator)

    def test_marathon_movies_relation(self):
        self.assertIn(self.movie, self.marathon.movies.all())

    def test_marathon_participants_relation(self):
        self.assertIn(self.participant,
                      self.marathon.participants.all())


class MarathonTicketModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="ticket_user",
            password="12345"
        )

        self.marathon = Marathon.objects.create(
            title="Ticket Marathon",
            description="Ticket description",
            start_date=timezone.now(),
            total_duration=90,
            curator=self.user
        )

        self.ticket = MarathonTicket.objects.create(
            user=self.user,
            marathon=self.marathon
        )

    def test_ticket_created(self):
        self.assertEqual(MarathonTicket.objects.count(), 1)

    def test_ticket_user_relation(self):
        self.assertEqual(self.ticket.user, self.user)

    def test_ticket_marathon_relation(self):
        self.assertEqual(self.ticket.marathon, self.marathon)

    def test_ticket_str(self):
        self.assertEqual(
            str(self.ticket),
            f"{self.user} → {self.marathon}"
        )
