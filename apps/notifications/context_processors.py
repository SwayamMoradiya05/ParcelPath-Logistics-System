from .models import Notification


def notification_context(request):
    if not request.user.is_authenticated:
        return {
            "notification_count": 0,
            "recent_notifications": [],
        }

    notifications = (
        Notification.objects.filter(
            user=request.user,
        )
        .order_by("-created_at")
    )

    return {
        "notification_count": notifications.filter(
            is_read=False,
        ).count(),
        "recent_notifications": notifications[:5],
    }