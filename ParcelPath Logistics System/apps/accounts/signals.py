from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from apps.accounts.models import User, UserRole, LoginHistory
from apps.customers.models import Customer


# ============================================================
# CREATE CUSTOMER PROFILE
# ============================================================

@receiver(post_save, sender=User)
def create_customer_profile(sender, instance, created, **kwargs):

    if created and instance.role == UserRole.CUSTOMER:

        Customer.objects.create(
            user=instance,
            address_line_1="Pending",
            city="Pending",
            state="Pending",
            postal_code="000000",
        )


# ============================================================
# LOGIN HISTORY
# ============================================================

@receiver(user_logged_in)
def record_user_login(sender, request, user, **kwargs):

    ip_address = request.META.get(
        "HTTP_X_FORWARDED_FOR"
    )

    if ip_address:
        ip_address = ip_address.split(",")[0].strip()
    else:
        ip_address = request.META.get(
            "REMOTE_ADDR"
        )

    user_agent = request.META.get(
        "HTTP_USER_AGENT",
        "",
    )

    LoginHistory.objects.create(
        user=user,
        ip_address=ip_address or "0.0.0.0",
        user_agent=user_agent,
        successful=True,
    )

    # Update user's online status
    user.is_online = True
    user.last_seen = timezone.now()

    user.save(
        update_fields=[
            "is_online",
            "last_seen",
        ]
    )


# ============================================================
# LOGOUT HISTORY
# ============================================================

@receiver(user_logged_out)
def record_user_logout(sender, request, user, **kwargs):

    if not user:
        return

    last_login = (
        LoginHistory.objects
        .filter(
            user=user,
            logout_time__isnull=True,
        )
        .order_by("-login_time")
        .first()
    )

    if last_login:
        last_login.logout_time = timezone.now()
        last_login.save(
            update_fields=[
                "logout_time",
            ]
        )

    user.is_online = False
    user.last_seen = timezone.now()

    user.save(
        update_fields=[
            "is_online",
            "last_seen",
        ]
    )