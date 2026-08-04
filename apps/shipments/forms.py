from datetime import date

from django import forms
from django.core.exceptions import ValidationError

from .models import Shipment


class ShipmentForm(forms.ModelForm):
    class Meta:
        model = Shipment

        exclude = (
            "tracking_number",
            "customer",
            "created_by",
            "status",
            "driver",
            "created_at",
            "updated_at",
            "delivered_at",
            "proof_of_delivery",
        )

        widgets = {
            "customer": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "sender_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Sender Name",
                }
            ),
            "sender_phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Sender Phone",
                }
            ),
            "sender_address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Sender Address",
                }
            ),
            "receiver_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Receiver Name",
                }
            ),
            "receiver_phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Receiver Phone",
                }
            ),
            "receiver_address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Receiver Address",
                }
            ),
            "package_type": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Package Type",
                }
            ),
            "weight": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0.1",
                }
            ),
            "length": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0.1",
                }
            ),
            "width": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0.1",
                }
            ),
            "height": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0.1",
                }
            ),
            "declared_value": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "shipping_cost": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "expected_delivery": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),
            "remarks": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Remarks",
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

    def clean_sender_name(self):
        return (
            self.cleaned_data["sender_name"]
            .strip()
            .title()
        )

    def clean_receiver_name(self):
        return (
            self.cleaned_data["receiver_name"]
            .strip()
            .title()
        )

    def clean_sender_phone(self):
        return (
            self.cleaned_data["sender_phone"]
            .strip()
        )

    def clean_receiver_phone(self):
        return (
            self.cleaned_data["receiver_phone"]
            .strip()
        )

    def clean_package_type(self):
        return (
            self.cleaned_data["package_type"]
            .strip()
            .title()
        )

    def clean_weight(self):
        weight = self.cleaned_data["weight"]

        if weight <= 0:
            raise ValidationError(
                "Weight must be greater than zero."
            )

        return weight

    def clean_length(self):
        length = self.cleaned_data["length"]

        if length <= 0:
            raise ValidationError(
                "Length must be greater than zero."
            )

        return length

    def clean_width(self):
        width = self.cleaned_data["width"]

        if width <= 0:
            raise ValidationError(
                "Width must be greater than zero."
            )

        return width

    def clean_height(self):
        height = self.cleaned_data["height"]

        if height <= 0:
            raise ValidationError(
                "Height must be greater than zero."
            )

        return height

    def clean_expected_delivery(self):
        delivery = self.cleaned_data.get(
            "expected_delivery"
        )

        if (
            delivery
            and delivery < date.today()
        ):
            raise ValidationError(
                "Expected delivery date cannot be in the past."
            )

        return delivery

    def clean(self):
        cleaned_data = super().clean()

        sender = cleaned_data.get(
            "sender_address"
        )
        receiver = cleaned_data.get(
            "receiver_address"
        )

        if (
            sender
            and receiver
            and sender.strip().lower()
            == receiver.strip().lower()
        ):
            raise ValidationError(
                "Sender and receiver addresses cannot be identical."
            )

        return cleaned_data

    def save(self, commit=True):
        shipment = super().save(commit=False)

        shipment.sender_name = (
            shipment.sender_name.strip().title()
        )

        shipment.receiver_name = (
            shipment.receiver_name.strip().title()
        )

        shipment.sender_phone = (
            shipment.sender_phone.strip()
        )

        shipment.receiver_phone = (
            shipment.receiver_phone.strip()
        )

        shipment.package_type = (
            shipment.package_type.strip().title()
        )

        if commit:
            shipment.save()

        return shipment