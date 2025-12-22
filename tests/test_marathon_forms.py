from django.test import TestCase
from django.utils import timezone

from marathons.forms import MarathonForm


class MarathonFormTest(TestCase):

    def test_form_valid_data(self):
        form = MarathonForm(
            data={
                "title": "Test Marathon",
                "description": "Some description",
                "start_date": timezone.now(),
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
        form = MarathonForm(
            data={
                "title": "Test Marathon",
                "description": "Description",
                "start_date": timezone.now(),
                "total_duration": "abc",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("total_duration", form.errors)

    def test_start_date_widget_type(self):
        form = MarathonForm()
        self.assertEqual(
            form.fields["start_date"].widget.input_type,
            "datetime-local"
        )
