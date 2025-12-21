from django import forms
from .models import Marathon


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
            "start_date": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"}
            ),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "total_duration": forms.NumberInput(attrs={"class": "form-control"}),
        }
