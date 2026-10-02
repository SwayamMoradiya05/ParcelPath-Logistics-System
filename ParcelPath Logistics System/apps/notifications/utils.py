from django.utils import timezone

from .models import Notification


def unread_notifications(user):
    if not user.is_authenticated:
        return Notification.objects.none()

    return Notification.objects.filter(
        user=user,
        is_read=False,
    )


def recent_notifications(
    user,
    limit=10,
):
    if not user.is_authenticated:
        return Notification.objects.none()

    return Notification.objects.filter(
        user=user,
    ).order_by(
        "-created_at",
    )[:limit]


def mark_as_read(notification):
    if notification.is_read:
        return notification

    notification.is_read = True
    notification.read_at = timezone.now()

    notification.save(
        update_fields=[
            "is_read",
            "read_at",
        ]
    )

    return notification


def mark_all_as_read(user):
    Notification.objects.filter(
        user=user,
        is_read=False,
    ).update(
        is_read=True,
        read_at=timezone.now(),
    )