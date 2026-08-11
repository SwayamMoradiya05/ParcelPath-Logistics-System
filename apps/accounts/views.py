from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.db import transaction
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
import secrets
from datetime import timedelta
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .forms import (
    LoginForm,
    ProfileUpdateForm,
    UserRegistrationForm,
)
from .models import User, UserRole,EmailVerificationToken
from apps.drivers.models import Driver


def redirect_user(user):
    """
    After login, send every user to the public home page.
    """

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
        if form.is_valid():

            try:
                with transaction.atomic():

                    user = form.save(commit=False)

                    # Account remains inactive until email is verified
                    user.is_active = False
                    user.email_verified = False
                    user.save()

                    # Remove any old verification tokens
                    EmailVerificationToken.objects.filter(
                        user=user
                    ).delete()

                    # Generate 6-digit OTP
                    otp = f"{secrets.randbelow(1000000):06d}"

                    # Store hashed OTP
                    from django.contrib.auth.hashers import make_password

                    verification_token = EmailVerificationToken.objects.create(
                        user=user,
                        token=make_password(otp),
                        expires_at=timezone.now() + timedelta(minutes=10),
                    )

                    # Store user ID in session
                    request.session["pending_verification_user_id"] = user.pk

                    # Send OTP email
                    send_mail(
                        subject="Verify Your ParcelPath Email",
                        message=(
                            f"Hello {user.first_name},\n\n"
                            f"Thank you for registering with ParcelPath.\n\n"
                            f"Your email verification OTP is:\n\n"
                            f"{otp}\n\n"
                            f"This OTP is valid for 10 minutes.\n\n"
                            f"Please do not share this OTP with anyone.\n\n"
                            f"Regards,\n"
                            f"ParcelPath Team"
                        ),
                        from_email=getattr(
                            settings,
                            "DEFAULT_FROM_EMAIL",
                            None,
                        ),
                        recipient_list=[user.email],
                        fail_silently=False,
                    )

                messages.success(
                    request,
                    "A verification OTP has been sent to your email address.",
                )

                return redirect("accounts:verify_email")

            except Exception as exc:
                print("REGISTRATION ERROR:", exc)

                messages.error(
                    request,
                    "Unable to send the verification email. Please try again.",
                )

    return render(
        request,
        "accounts/register.html",
        {
            "form": form,
        },
    )

def verify_email_view(request):
    user_id = request.session.get(
        "pending_verification_user_id"
    )

    if not user_id:
        messages.error(
            request,
            "Your verification session has expired. Please register again.",
        )
        return redirect("accounts:register")

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        request.session.pop(
            "pending_verification_user_id",
            None,
        )

        messages.error(
            request,
            "User account not found. Please register again.",
        )

        return redirect("accounts:register")

    if user.email_verified:
        request.session.pop(
            "pending_verification_user_id",
            None,
        )

        return redirect_user(user)

    if request.method == "POST":

        otp = request.POST.get("otp", "").strip()

        if not otp:
            messages.error(
                request,
                "Please enter the verification OTP.",
            )

        elif len(otp) != 6 or not otp.isdigit():
            messages.error(
                request,
                "OTP must be a 6-digit number.",
            )

        else:
            token = (
                EmailVerificationToken.objects
                .filter(
                    user=user,
                    is_used=False,
                )
                .order_by("-created_at")
                .first()
            )

            if not token:
                messages.error(
                    request,
                    "Verification OTP not found. Please request a new OTP.",
                )

            elif token.is_expired:
                messages.error(
                    request,
                    "Your OTP has expired. Please request a new OTP.",
                )

            else:
                from django.contrib.auth.hashers import check_password

                if not check_password(
                    otp,
                    token.token,
                ):
                    messages.error(
                        request,
                        "Invalid verification OTP.",
                    )

                else:
                    with transaction.atomic():

                        user.email_verified = True
                        user.is_active = True
                        user.save(
                            update_fields=[
                                "email_verified",
                                "is_active",
                                "updated_at",
                            ]
                        )

                        token.is_used = True
                        token.save(
                            update_fields=["is_used"]
                        )

                        # Create customer profile
                        if user.role == UserRole.CUSTOMER:
                            from apps.customers.models import Customer

                            Customer.objects.get_or_create(
                                user=user,
                                defaults={
                                    "address_line_1": "",
                                    "city": "",
                                    "state": "",
                                    "postal_code": "",
                                },
                            )

                    request.session.pop(
                        "pending_verification_user_id",
                        None,
                    )

                    # Successful registration email
                    try:
                        send_mail(
                            subject="Welcome to ParcelPath - Registration Successful",
                            message=(
                                f"Hello {user.first_name},\n\n"
                                f"Your ParcelPath account has been successfully "
                                f"verified and registered.\n\n"
                                f"Account Details:\n"
                                f"Name: {user.full_name}\n"
                                f"Email: {user.email}\n"
                                f"Phone: {user.phone}\n"
                                f"Account Type: {user.get_role_display()}\n\n"
                                f"You can now log in to your ParcelPath account.\n\n"
                                f"Thank you for choosing ParcelPath.\n\n"
                                f"Regards,\n"
                                f"ParcelPath Team"
                            ),
                            from_email=getattr(
                                settings,
                                "DEFAULT_FROM_EMAIL",
                                None,
                            ),
                            recipient_list=[user.email],
                            fail_silently=True,
                        )

                    except Exception as exc:
                        print(
                            "SUCCESS EMAIL ERROR:",
                            exc,
                        )

                    messages.success(
                        request,
                        "Email verified successfully. Your account has been created.",
                    )

                    login(
                        request,
                        user,
                    )

                    return redirect_user(user)

    return render(
        request,
        "accounts/verify_email.html",
        {
            "user": user,
        },
    )

def resend_verification_otp(request):
    user_id = request.session.get(
        "pending_verification_user_id"
    )

    if not user_id:
        messages.error(
            request,
            "Your verification session has expired. Please register again.",
        )

        return redirect("accounts:register")

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        messages.error(
            request,
            "User account not found.",
        )

        return redirect("accounts:register")

    if user.email_verified:
        return redirect_user(user)

    EmailVerificationToken.objects.filter(
        user=user,
        is_used=False,
    ).update(
        is_used=True
    )

    otp = f"{secrets.randbelow(1000000):06d}"

    from django.contrib.auth.hashers import make_password

    EmailVerificationToken.objects.create(
        user=user,
        token=make_password(otp),
        expires_at=timezone.now() + timedelta(minutes=10),
    )

    try:
        send_mail(
            subject="Your New ParcelPath Verification OTP",
            message=(
                f"Hello {user.first_name},\n\n"
                f"Your new ParcelPath email verification OTP is:\n\n"
                f"{otp}\n\n"
                f"This OTP is valid for 10 minutes.\n\n"
                f"Regards,\n"
                f"ParcelPath Team"
            ),
            from_email=getattr(
                settings,
                "DEFAULT_FROM_EMAIL",
                None,
            ),
            recipient_list=[user.email],
            fail_silently=False,
        )

        messages.success(
            request,
            "A new verification OTP has been sent to your email.",
        )

    except Exception as exc:
        print(
            "RESEND OTP ERROR:",
            exc,
        )

        messages.error(
            request,
            "Unable to send OTP. Please try again later.",
        )

    return redirect("accounts:verify_email")


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

