from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.db import transaction
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST


from .forms import (
    LoginForm,
    ProfileUpdateForm,
    UserRegistrationForm,
)
from .models import UserRole
from apps.drivers.models import Driver


def redirect_user(user):
    """
    Redirect users based on role.
    """

    if user.is_superuser or user.is_staff or user.role == UserRole.ADMIN:
        return redirect("dashboard:dashboard")

    if user.role == UserRole.CUSTOMER:
        return redirect("customers:dashboard")

    if user.role == UserRole.DRIVER:
        try:
            driver = Driver.objects.get(user=user)

            if (
                not driver.license_number
                or not driver.vehicle_number
            ):
                return redirect("drivers:complete_profile")

            return redirect("drivers:dashboard")

        except Driver.DoesNotExist:
            return redirect("drivers:complete_profile")

    return redirect("home")

def login_view(request):
    if request.user.is_authenticated:
        print("Already authenticated")
        return redirect_user(request.user)

    form = LoginForm(request.POST or None)

    if request.method == "POST":
        print("POST received")

        if form.is_valid():
            print("Form is valid")

            user = form.cleaned_data["user"]
            print("User:", user.email)
            print("Role:", user.role)

            login(request, user)

            print("Authenticated:", request.user.is_authenticated)
            print("Session:", request.session.session_key)

            return redirect_user(user)
        else:
            print("FORM ERRORS:", form.errors)

    return render(
        request,
        "accounts/login.html",
        {"form": form},
    )


@login_required
def logout_view(request):
    """
    Safely logs out the current user.

    Supports both GET and POST during development.
    Once every template uses a POST form,
    this can be changed back to POST-only.
    """

    if request.user.is_authenticated:
        logout(request)
        messages.success(
            request,
            "You have been logged out successfully."
        )

    return redirect("home")


def register_view(request):
    if request.user.is_authenticated:
        return redirect_user(request.user)

    form = UserRegistrationForm(request.POST or None)

    if request.method == "POST":
        print("REGISTER POST RECEIVED")

        if form.is_valid():
            user = form.save()

            from apps.accounts.models import UserRole
            from apps.customers.models import Customer

            # Automatically create Customer profile
            if user.role == UserRole.CUSTOMER:
                Customer.objects.get_or_create(
                    user=user,
                    defaults={
                        "address_line_1": "",
                        "city": "",
                        "state": "",
                        "postal_code": "",
                    },
                )

            messages.success(
                request,
                "Registration successful."
            )

            login(request, user)

            return redirect_user(user)

        else:
            print("REGISTER ERRORS:")
            print(form.errors)
            print(form.non_field_errors())

    return render(
        request,
        "accounts/register.html",
        {
            "form": form,
        },
    )


@login_required
def profile_view(request):
    """
    View User Profile
    """

    return render(
        request,
        "accounts/profile.html",
        {
            "user_obj": request.user,
        },
    )


@login_required
def edit_profile_view(request):
    """
    Edit User Profile
    """

    form = ProfileUpdateForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user,
    )

    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            form.save()

        messages.success(
            request,
            "Your profile has been updated successfully.",
        )

        return redirect("accounts:profile")

    return render(
        request,
        "accounts/edit_profile.html",
        {
            "form": form,
        },
    )


@login_required
def change_password_view(request):
    """
    Change Password
    """

    form = PasswordChangeForm(
        request.user,
        request.POST or None,
    )

    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            user = form.save()

        update_session_auth_hash(
            request,
            user,
        )

        messages.success(
            request,
            "Your password has been changed successfully.",
        )

        return redirect("accounts:profile")

    return render(
        request,
        "accounts/change_password.html",
        {
            "form": form,
        },
    )

from django.http import HttpResponse
from .models import User, UserRole


def create_render_admin(request):

    SECRET = "parcelpath-create-admin-2026"

    if request.GET.get("key") != SECRET:
        return HttpResponse(
            "Unauthorized",
            status=403,
        )

    email = "admin@gmail.com"

    if User.objects.filter(email=email).exists():
        return HttpResponse(
            "Admin already exists.",
        )

    admin = User.objects.create_superuser(
        username="admin",
        email=email,
        password="Admin@12345",
    )

    admin.role = UserRole.ADMIN
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()

    return HttpResponse(
        "Superuser created successfully."
    )