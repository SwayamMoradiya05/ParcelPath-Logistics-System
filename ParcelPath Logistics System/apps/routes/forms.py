from django import forms
from django.core.exceptions import ValidationError

from .models import Route


class RouteForm(forms.ModelForm):
    class Meta:
        model = Route

        exclude = (
            "route_code",
            "created_at",
            "updated_at",
        )

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Route Name",
                }
            ),
            "driver": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "origin": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Origin",
                }
            ),
            "destination": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Destination",
                }
            ),
            "total_distance": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "estimated_duration": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "placeholder": "Duration (minutes)",
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Additional Notes",
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

    def clean_name(self):
        return (
            self.cleaned_data["name"]
            .strip()
            .title()
        )

    def clean_origin(self):
        origin = (
            self.cleaned_data["origin"]
            .strip()
            .title()
        )

        if len(origin) < 3:
            raise ValidationError(
                "Origin must contain at least 3 characters."
            )

        return origin

    def clean_destination(self):
        destination = (
            self.cleaned_data["destination"]
            .strip()
            .title()
        )

        if len(destination) < 3:
            raise ValidationError(
                "Destination must contain at least 3 characters."
            )

        return destination

    def clean_total_distance(self):
        distance = self.cleaned_data["total_distance"]

        if distance < 0:
            raise ValidationError(
                "Distance cannot be negative."
            )

        return distance

    def clean_estimated_duration(self):
        duration = self.cleaned_data["estimated_duration"]

        if duration < 0:
            raise ValidationError(
                "Estimated duration cannot be negative."
            )

        return duration

    def clean(self):
        cleaned_data = super().clean()

        origin = cleaned_data.get("origin")
        destination = cleaned_data.get("destination")

        if (
            origin
            and destination
            and origin.strip().lower()
            == destination.strip().lower()
        ):
            raise ValidationError(
                "Origin and destination cannot be the same."
            )

        return cleaned_data

    def save(self, commit=True):
        route = super().save(commit=False)

        route.name = route.name.strip().title()
        route.origin = route.origin.strip().title()
        route.destination = route.destination.strip().title()

        if commit:
            route.save()

        return route