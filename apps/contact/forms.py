from django import forms

from .models import Contact


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact

        fields = (
            "name",
            "email",
            "phone",
            "subject",
            "category",
            "message",
        )

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Full Name",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Email Address",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Phone Number",
                }
            ),
            "subject": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Subject",
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Write your message...",
                }
            ),
        }

    def clean_name(self):
        name = self.cleaned_data["name"].strip()

        if len(name) < 3:
            raise forms.ValidationError(
                "Name must be at least 3 characters."
            )

        return name.title()

    def clean_subject(self):
        subject = self.cleaned_data["subject"].strip()

        if len(subject) < 5:
            raise forms.ValidationError(
                "Subject must be at least 5 characters."
            )

        return subject

    def clean_phone(self):
        phone = self.cleaned_data.get(
            "phone",
            "",
        ).strip()

        if phone:
            digits = phone.replace("+", "").replace("-", "").replace(" ", "")

            if not digits.isdigit():
                raise forms.ValidationError(
                    "Enter a valid phone number."
                )

            if len(digits) < 10:
                raise forms.ValidationError(
                    "Phone number must contain at least 10 digits."
                )

        return phone

    def clean_message(self):
        message = self.cleaned_data["message"].strip()

        if len(message) < 10:
            raise forms.ValidationError(
                "Message must be at least 10 characters."
            )

        return message

    def save(self, commit=True):
        contact = super().save(commit=False)

        contact.name = contact.name.strip()
        contact.subject = contact.subject.strip()
        contact.message = contact.message.strip()

        if commit:
            contact.save()

        return contact


class ContactReplyForm(forms.ModelForm):
    class Meta:
        model = Contact

        fields = (
            "admin_reply",
            "status",
        )

        widgets = {
            "admin_reply": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Write your reply...",
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
        }

    def clean_admin_reply(self):
        reply = self.cleaned_data["admin_reply"].strip()

        if len(reply) < 5:
            raise forms.ValidationError(
                "Reply must be at least 5 characters."
            )

        return reply