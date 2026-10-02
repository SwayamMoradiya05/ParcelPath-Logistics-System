from django import forms

from .models import Destination


class DestinationForm(forms.ModelForm):
    class Meta:
        model = Destination

        fields = (
            "name",
            "city",
            "state",
            "country",
            "postal_code",
            "address",
            "latitude",
            "longitude",
            "is_active",
        )

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Destination Name",
                }
            ),
            "city": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "City",
                }
            ),
            "state": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "State",
                }
            ),
            "country": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Country",
                }
            ),
            "postal_code": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Postal Code",
                }
            ),
            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Complete Address",
                }
            ),
            "latitude": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.000001",
                    "placeholder": "Latitude",
                }
            ),
            "longitude": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.000001",
                    "placeholder": "Longitude",
                }
            ),
            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }

    def clean_name(self):
        name = self.cleaned_data["name"].strip()

        if len(name) < 3:
            raise forms.ValidationError(
                "Destination name must be at least 3 characters."
            )

        return name.title()

    def clean_city(self):
        return self.cleaned_data["city"].strip().title()

    def clean_state(self):
        return self.cleaned_data["state"].strip().title()

    def clean_country(self):
        return self.cleaned_data["country"].strip().title()

    def clean_postal_code(self):
        postal_code = self.cleaned_data["postal_code"].strip().upper()

        if len(postal_code) < 4:
            raise forms.ValidationError(
                "Enter a valid postal code."
            )

        return postal_code

    def clean_address(self):
        address = self.cleaned_data["address"].strip()

        if len(address) < 10:
            raise forms.ValidationError(
                "Address must be at least 10 characters."
            )

        return address

    def clean(self):
        cleaned_data = super().clean()

        latitude = cleaned_data.get("latitude")
        longitude = cleaned_data.get("longitude")

        if latitude is not None:
            if latitude < -90 or latitude > 90:
                self.add_error(
                    "latitude",
                    "Latitude must be between -90 and 90.",
                )

        if longitude is not None:
            if longitude < -180 or longitude > 180:
                self.add_error(
                    "longitude",
                    "Longitude must be between -180 and 180.",
                )

        return cleaned_data

    def save(self, commit=True):
        destination = super().save(commit=False)

        destination.name = destination.name.strip()
        destination.city = destination.city.strip()
        destination.state = destination.state.strip()
        destination.country = destination.country.strip()
        destination.postal_code = destination.postal_code.strip().upper()
        destination.address = destination.address.strip()

        if commit:
            destination.save()

        return destination