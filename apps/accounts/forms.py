from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import re

from .models import User,UserRole


class LoginForm(forms.Form):

    email = forms.EmailField(
        label="Email",
        error_messages={
            "required": "Please enter your email address.",
            "invalid": "Enter a valid email address.",
        },
    )

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(),
        error_messages={
            "required": "Please enter your password.",
        },
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.user = None

        self.fields["email"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Enter your email",
            "autocomplete": "email",
        })

        self.fields["password"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Enter your password",
            "autocomplete": "current-password",
        })

    def clean(self):
        cleaned_data = super().clean()

        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if not email or not password:
            return cleaned_data

        email = email.lower()

        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError(
                "No account exists with this email address."
            )

        self.user = authenticate(
            username=email,
            password=password,
        )

        if self.user is None:
            raise forms.ValidationError(
                "Incorrect email or password."
            )

        if not self.user.is_active:
            raise forms.ValidationError(
                "Your account has been disabled."
            )

        cleaned_data["user"] = self.user

        return cleaned_data


from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import User, UserRole


from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import User, UserRole


class UserRegistrationForm(UserCreationForm):

    first_name = forms.CharField(
        max_length=150,
        error_messages={
            "required": "First name is required.",
        },
    )

    last_name = forms.CharField(
        max_length=150,
        error_messages={
            "required": "Last name is required.",
        },
    )

    email = forms.EmailField(
        error_messages={
            "required": "Email address is required.",
            "invalid": "Enter a valid email address.",
        },
    )

    phone = forms.CharField(
        max_length=15,
        error_messages={
            "required": "Phone number is required.",
        },
    )

    role = forms.ChoiceField(
        choices=[
            (UserRole.CUSTOMER, "Customer"),
            (UserRole.DRIVER, "Driver"),
        ],
        error_messages={
            "required": "Please select an account type.",
        },
    )

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone",
            "role",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        placeholders = {
            "first_name": "Enter first name",
            "last_name": "Enter last name",
            "email": "Enter email address",
            "phone": "Enter phone number",
            "role": "Select account type",
            "password1": "Enter password",
            "password2": "Confirm password",
        }

        for field_name, field in self.fields.items():

            css = "form-control"

            if isinstance(field.widget, forms.Select):
                css = "form-select"

            field.widget.attrs.update({
                "class": css,
                "placeholder": placeholders.get(field_name, ""),
            })

        self.fields["password1"].help_text = (
            "Password must contain at least 8 characters and should not be too common."
        )

        self.fields["password2"].help_text = (
            "Enter the same password again for verification."
        )

    def clean_email(self):
        email = self.cleaned_data["email"].lower()

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()

        if not phone.isdigit():
            raise forms.ValidationError(
                "Phone number must contain only digits."
            )

        if len(phone) != 10:
            raise forms.ValidationError(
                "Phone number must be exactly 10 digits."
            )

        return phone

    def clean(self):
        cleaned_data = super().clean()

        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error(
                "password2",
                "Passwords do not match."
            )

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        user.email = self.cleaned_data["email"].lower()
        user.phone = self.cleaned_data["phone"]
        user.role = self.cleaned_data["role"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]

        if commit:
            user.save()

        return user


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User

        fields = [
            "first_name",
            "last_name",
            "phone",
            "profile_picture",
            "date_of_birth",
            "address",
            "city",
            "state",
            "country",
            "postal_code",
        ]

        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "phone": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),
            "city": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "state": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "country": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "postal_code": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "date_of_birth": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")

        if phone:
            phone = phone.strip()

            if not re.fullmatch(r"^[0-9]{10}$", phone):
                raise ValidationError(
                    "Enter a valid 10-digit phone number."
                )

        return phone

    def clean_profile_picture(self):
        picture = self.cleaned_data.get("profile_picture")

        if picture:
            if picture.size > 2 * 1024 * 1024:
                raise ValidationError(
                    "Profile picture must be smaller than 2 MB."
                )

        return picture


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
            }
        )
    )

    new_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
            }
        )
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
            }
        )
    )

    def clean(self):
        cleaned = super().clean()

        new_password = cleaned.get("new_password")
        confirm_password = cleaned.get("confirm_password")

        if new_password != confirm_password:
            raise ValidationError(
                "Passwords do not match."
            )

        if new_password:
            validate_password(new_password)

        return cleaned