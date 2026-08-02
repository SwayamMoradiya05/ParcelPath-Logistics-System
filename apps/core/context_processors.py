from django.utils import timezone


def global_settings(request):
    return {
        "APP_NAME": "ParcelPath",
        "CURRENT_YEAR": timezone.now().year,
    }


def notification_context(request):
    unread_count = 0

    if request.user.is_authenticated:
        try:
            from apps.notifications.models import Notification

            unread_count = Notification.objects.filter(
                user=request.user,
                is_read=False,
            ).count()
        except Exception:
            unread_count = 0

    return {
        "UNREAD_NOTIFICATIONS": unread_count,
    }