from datetime import timedelta
from django.test import TestCase
from django.utils import timezone

from marathons.forms import MarathonForm


class MarathonFormTest(TestCase):
    def test_form_valid_data(self):
        start_date = timezone.now() + timedelta(days=1, hours=1)
        form = MarathonForm(
            data={
                "title": "Test Marathon",
                "description": "Some description",
                "start_date": start_date.strftime("%Y-%m-%dT%H:%M"),
                "total_duration": 180,
            }
        )
        self.assertTrue(form.is_valid())

    def test_form_missing_required_fields(self):
        form = MarathonForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)
        self.assertIn("start_date", form.errors)
        self.assertIn("total_duration", form.errors)

    def test_total_duration_must_be_integer(self):
        start_date = timezone.now() + timedelta(days=1, hours=1)
        form = MarathonForm(
            data={
                "title": "Test Marathon",
                "description": "Description",
                "start_date": start_date.strftime("%Y-%m-%dT%H:%M"),
                "total_duration": "abc",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("total_duration", form.errors)

    def test_start_date_cannot_be_today(self):
        today = timezone.now()
        form = MarathonForm(
            data={
                "title": "Test Marathon",
                "description": "Desc",
                "start_date": today.strftime("%Y-%m-%dT%H:%M"),
                "total_duration": 60,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("start_date", form.errors)

    def test_start_date_widget_type(self):
        form = MarathonForm()
        self.assertEqual(
            form.fields["start_date"].widget.input_type,
            "datetime-local"
        )
