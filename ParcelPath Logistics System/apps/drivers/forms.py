from datetime import date

from django import forms
from django.core.exceptions import ValidationError

from .models import Driver


class DriverForm(forms.ModelForm):

    class Meta:
        model = Driver

        exclude = (
            "driver_id",
            "user",
            "status",
            "total_deliveries",
            "successful_deliveries",
            "cancelled_deliveries",
            "rating",
            "joined_date",
            "created_at",
            "updated_at",
        )

        widgets = {
            "license_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter license number",
                }
            ),
            "license_expiry": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),
            "vehicle_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "vehicle_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter vehicle number",
                }
            ),
            "vehicle_model": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Vehicle model",
                }
            ),
            "vehicle_capacity": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                }
            ),
            "alternate_phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Alternate phone",
                }
            ),
            "profile_image": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        placeholders = {
        "license_number": "Enter license number",
        "license_expiry": "",
        "vehicle_type": "",
        "vehicle_number": "Enter vehicle number",
        "vehicle_model": "Enter vehicle model",
        "vehicle_capacity": "Enter capacity (KG)",
        "alternate_phone": "Enter alternate phone number",
    }

        for name, field in self.fields.items():

            css = "form-control"

        if isinstance(field.widget, forms.Select):
            css = "form-select"

        if name in self.errors:
            css += " is-invalid"

        field.widget.attrs.update({
            "class": css,
            "placeholder": placeholders.get(name, ""),
        })

    def clean_license_number(self):
        license_number = (
            self.cleaned_data.get(
                "license_number",
                "",
            )
            .upper()
            .strip()
        )

        return license_number

    def clean_vehicle_number(self):
        vehicle_number = (
            self.cleaned_data.get(
                "vehicle_number",
                "",
            )
            .upper()
            .strip()
        )

        return vehicle_number

    def clean_vehicle_capacity(self):
        capacity = self.cleaned_data.get(
            "vehicle_capacity"
        )

        if capacity <= 0:
            raise ValidationError(
                "Vehicle capacity must be greater than zero."
            )

        return capacity

    def clean_license_expiry(self):
        expiry = self.cleaned_data.get(
            "license_expiry"
        )

        if expiry <= date.today():
            raise ValidationError(
                "License expiry date must be in the future."
            )

        return expiry

    def clean_alternate_phone(self):
        phone = (
            self.cleaned_data.get(
                "alternate_phone",
                "",
            )
            .strip()
        )

        return phone

    def clean_profile_image(self):
        image = self.cleaned_data.get(
            "profile_image"
        )

        if not image:
            return image

        if image.size > 2 * 1024 * 1024:
            raise ValidationError(
                "Image size cannot exceed 2 MB."
            )

        allowed_extensions = (
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
        )

        if not image.name.lower().endswith(
            allowed_extensions
        ):
            raise ValidationError(
                "Only JPG, JPEG, PNG and WEBP images are allowed."
            )

        return image

    def clean(self):
        cleaned_data = super().clean()

        latitude = cleaned_data.get(
            "current_latitude"
        )

        longitude = cleaned_data.get(
            "current_longitude"
        )

        if (
            latitude is not None
            and not (-90 <= latitude <= 90)
        ):
            self.add_error(
                "current_latitude",
                "Latitude must be between -90 and 90.",
            )

        if (
            longitude is not None
            and not (-180 <= longitude <= 180)
        ):
            self.add_error(
                "current_longitude",
                "Longitude must be between -180 and 180.",
            )

        return cleaned_data

    def save(self, commit=True):
        driver = super().save(commit=False)

        driver.status = Driver.Status.AVAILABLE

        driver.license_number = driver.license_number.upper().strip()
        driver.vehicle_number = driver.vehicle_number.upper().strip()

        if driver.alternate_phone:
            driver.alternate_phone = driver.alternate_phone.strip()

        if commit:
            driver.save()

        return driver