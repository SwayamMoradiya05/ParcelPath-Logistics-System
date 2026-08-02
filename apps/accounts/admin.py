from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    EmailVerificationToken,
    LoginHistory,
    PasswordResetToken,
    User,
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    ordering = ("email",)

    list_display = (
        "email",
        "full_name",
        "role",
        "is_active",
        "is_staff",
        "email_verified",
        "phone_verified",
        "last_login",
        "created_at",
    )

    list_filter = (
        "role",
        "is_active",
        "is_staff",
        "is_superuser",
        "email_verified",
        "phone_verified",
        "created_at",
        "last_login",
    )

    search_fields = (
        "email",
        "first_name",
        "last_name",
        "phone",
    )

    readonly_fields = (
        "last_login",
        "last_seen",
        "created_at",
        "updated_at",
        "failed_login_attempts",
        "account_locked_until",
    )

    date_hierarchy = "created_at"

    list_per_page = 25

    fieldsets = (
        (
            "Authentication",
            {
                "fields": (
                    "email",
                    "password",
                )
            },
        ),
        (
            "Personal Information",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "phone",
                    "profile_picture",
                    "date_of_birth",
                )
            },
        ),
        (
            "Address",
            {
                "classes": ("collapse",),
                "fields": (
                    "address",
                    "city",
                    "state",
                    "country",
                    "postal_code",
                ),
            },
        ),
        (
            "Role & Permissions",
            {
                "fields": (
                    "role",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            "Verification",
            {
                "classes": ("collapse",),
                "fields": (
                    "email_verified",
                    "phone_verified",
                ),
            },
        ),
        (
            "Security",
            {
                "classes": ("collapse",),
                "fields": (
                    "failed_login_attempts",
                    "account_locked_until",
                    "last_login",
                    "last_seen",
                ),
            },
        ),
        (
            "Important Dates",
            {
                "classes": ("collapse",),
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "role",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "ip_address",
        "user_agent",
        "successful",
        "login_time",
    )

    search_fields = (
        "user__email",
        "user__first_name",
        "user__last_name",
        "ip_address",
    )

    list_filter = (
        "successful",
        "login_time",
    )

    ordering = (
        "-login_time",
    )

    readonly_fields = (
        "login_time",
    )

    date_hierarchy = "login_time"

    list_per_page = 50


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "token",
        "expires_at",
        "is_used",
        "created_at",
    )

    search_fields = (
        "user__email",
        "token",
    )

    list_filter = (
        "is_used",
        "expires_at",
    )

    readonly_fields = (
        "token",
        "created_at",
    )

    ordering = (
        "-created_at",
    )


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "token",
        "expires_at",
        "is_used",
        "created_at",
    )

    search_fields = (
        "user__email",
        "token",
    )

    list_filter = (
        "is_used",
        "expires_at",
    )

    readonly_fields = (
        "token",
        "created_at",
    )

    ordering = (
        "-created_at",
    )