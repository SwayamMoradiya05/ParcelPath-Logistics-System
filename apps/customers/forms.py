from django import forms
from django.core.exceptions import ValidationError

from .models import Customer


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer

        exclude = (
            "customer_id",
            "user",
            "total_shipments",
            "completed_shipments",
            "cancelled_shipments",
            "created_at",
            "updated_at",
        )

        widgets = {
            "company_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter company name",
                }
            ),
            "gst_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter GST number",
                }
            ),
            "alternate_phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter alternate phone",
                }
            ),
            "profile_image": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "address_line_1": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Address Line 1",
                }
            ),
            "address_line_2": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Address Line 2",
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
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Additional notes",
                }
            ),
            "is_verified": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def clean_company_name(self):
        company = self.cleaned_data.get("company_name", "").strip()
        return company

    def clean_gst_number(self):
        gst = self.cleaned_data.get("gst_number", "").strip().upper()

        if gst and len(gst) != 15:
            raise ValidationError(
                "GST number must be exactly 15 characters."
            )

        return gst

    def clean_alternate_phone(self):
        phone = self.cleaned_data.get("alternate_phone", "").strip()

        return phone

    def clean_postal_code(self):
        postal_code = self.cleaned_data.get("postal_code", "").strip()

        if not postal_code.isdigit():
            raise ValidationError(
                "Postal code must contain only digits."
            )

        if len(postal_code) not in (5, 6):
            raise ValidationError(
                "Postal code must be 5 or 6 digits."
            )

        return postal_code

    def clean_profile_image(self):
        image = self.cleaned_data.get("profile_image")

        if not image:
            return image

        if image.size > 2 * 1024 * 1024:
            raise ValidationError(
                "Image size cannot exceed 2 MB."
            )

        valid_extensions = (
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
        )

        if not image.name.lower().endswith(valid_extensions):
            raise ValidationError(
                "Only JPG, JPEG, PNG and WEBP images are allowed."
            )

        return image

    def clean(self):
        cleaned_data = super().clean()

        address = cleaned_data.get("address_line_1")
        city = cleaned_data.get("city")
        state = cleaned_data.get("state")
        country = cleaned_data.get("country")

        if not address:
            self.add_error(
                "address_line_1",
                "Address Line 1 is required.",
            )

        if city:
            cleaned_data["city"] = city.title()

        if state:
            cleaned_data["state"] = state.title()

        if country:
            cleaned_data["country"] = country.title()

        return cleaned_data

    def save(self, commit=True):
        customer = super().save(commit=False)

        customer.company_name = customer.company_name.strip()

        if customer.gst_number:
            customer.gst_number = customer.gst_number.upper().strip()

        if customer.alternate_phone:
            customer.alternate_phone = customer.alternate_phone.strip()

        if commit:
            customer.save()

        return customer