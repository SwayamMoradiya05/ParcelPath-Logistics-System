from django import forms
from django.core.exceptions import ValidationError

from .models import TrackingEvent


class TrackingEventForm(forms.ModelForm):
    class Meta:
        model = TrackingEvent

        fields = (
            "status",
            "location",
            "description",
            "latitude",
            "longitude",
        )

        widgets = {
            "status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "location": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Current Location",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Tracking Description",
                }
            ),
            "latitude": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.0000001",
                    "placeholder": "Latitude",
                }
            ),
            "longitude": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.0000001",
                    "placeholder": "Longitude",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.setdefault(
                "class",
                "form-control",
            )

    def clean_location(self):
        location = (
            self.cleaned_data["location"]
            .strip()
            .title()
        )

        if len(location) < 3:
            raise ValidationError(
                "Location must contain at least 3 characters."
            )

        return location

    def clean_description(self):
        description = (
            self.cleaned_data["description"]
            .strip()
        )

        if len(description) < 5:
            raise ValidationError(
                "Description is too short."
            )

        return description

    def clean(self):
        cleaned_data = super().clean()

        latitude = cleaned_data.get("latitude")
        longitude = cleaned_data.get("longitude")

        if (
            latitude is None
        ) != (
            longitude is None
        ):
            raise ValidationError(
                "Latitude and Longitude must be provided together."
            )

        if latitude is not None:
            if latitude < -90 or latitude > 90:
                raise ValidationError(
                    "Latitude must be between -90 and 90."
                )

        if longitude is not None:
            if longitude < -180 or longitude > 180:
                raise ValidationError(
                    "Longitude must be between -180 and 180."
                )

        return cleaned_data

    def save(self, commit=True):
        tracking = super().save(commit=False)

        tracking.location = (
            tracking.location.strip().title()
        )

        tracking.description = (
            tracking.description.strip()
        )

        if commit:
            tracking.save()

        return tracking