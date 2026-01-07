from datetime import timedelta, datetime
from django import forms
from django.utils import timezone

from marathons.models import Marathon


class MarathonForm(forms.ModelForm):
    class Meta:
        model = Marathon
        fields = [
            "title",
            "description",
            "start_date",
            "total_duration",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Marathon title",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Short description",
                }
            ),
            "start_date": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M",
                attrs={
                    "type": "datetime-local",
                    "class": "form-control",
                }
            ),
            "total_duration": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        tomorrow = (timezone.now() + timedelta(days=1)).date()
        min_dt = datetime.combine(tomorrow, datetime.min.time())

        self.fields["start_date"].widget.attrs.update({
            "min": min_dt.strftime("%Y-%m-%dT%H:%M"),
            "step": "60",
        })

    def clean_start_date(self):
        start_date = self.cleaned_data["start_date"]

        if timezone.is_naive(start_date):
            start_date = timezone.make_aware(
                start_date,
                timezone.get_current_timezone(),
            )

        tomorrow = (timezone.now() + timedelta(days=1)).date()
        min_dt = timezone.make_aware(
            datetime.combine(tomorrow, datetime.min.time()),
            timezone.get_current_timezone(),
        )

        if start_date < min_dt:
            raise forms.ValidationError(
                "Marathon can be created only starting from tomorrow."
            )

        return start_date
