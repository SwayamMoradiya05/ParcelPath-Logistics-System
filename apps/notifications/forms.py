from django import forms

from .models import Notification


class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification

        fields = (
            "title",
            "message",
            "notification_type",
            "action_url",
        )

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Notification title",
                    "maxlength": 200,
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Notification message",
                }
            ),
            "notification_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "action_url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://example.com/page",
                }
            ),
        }

    def clean_title(self):
        title = self.cleaned_data["title"].strip()

        if len(title) < 3:
            raise forms.ValidationError(
                "Title must contain at least 3 characters."
            )

        return title

    def clean_message(self):
        message = self.cleaned_data["message"].strip()

        if len(message) < 5:
            raise forms.ValidationError(
                "Message must contain at least 5 characters."
            )

        return message

    def clean_action_url(self):
        url = self.cleaned_data.get("action_url", "").strip()

        return url

    def save(self, commit=True):
        notification = super().save(commit=False)

        notification.title = notification.title.strip()
        notification.message = notification.message.strip()

        if commit:
            notification.save()

        return notification


class NotificationReadForm(forms.ModelForm):
    """
    Lightweight form for updating read/unread status.
    """

    class Meta:
        model = Notification

        fields = (
            "is_read",
        )

    def save(self, commit=True):
        notification = super().save(commit=False)

        if notification.is_read:
            notification.mark_as_read()
        else:
            notification.mark_as_unread()

        return notification