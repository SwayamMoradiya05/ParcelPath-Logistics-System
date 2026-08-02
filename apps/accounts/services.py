import secrets
from datetime import timedelta

from django.utils import timezone

from .models import (
    EmailVerificationToken,
    LoginHistory,
    PasswordResetToken,
)


class AccountService:

    @staticmethod
    def create_email_token(user):
        return EmailVerificationToken.objects.create(
            user=user,
            token=secrets.token_urlsafe(48),
            expires_at=timezone.now() + timedelta(hours=24),
        )

    @staticmethod
    def create_password_reset_token(user):
        return PasswordResetToken.objects.create(
            user=user,
            token=secrets.token_urlsafe(48),
            expires_at=timezone.now() + timedelta(hours=1),
        )

    @staticmethod
    def verify_email(token):
        try:
            obj = EmailVerificationToken.objects.get(
                token=token,
                is_used=False,
            )

            if obj.is_expired:
                return False

            obj.is_used = True
            obj.save(update_fields=["is_used"])

            obj.user.email_verified = True
            obj.user.save(update_fields=["email_verified"])

            return True

        except EmailVerificationToken.DoesNotExist:
            return False

    @staticmethod
    def record_login(request, user, success=True):
        LoginHistory.objects.create(
            user=user,
            ip_address=request.META.get(
                "REMOTE_ADDR",
                "0.0.0.0",
            ),
            user_agent=request.META.get(
                "HTTP_USER_AGENT",
                "",
            ),
            successful=success,
        )