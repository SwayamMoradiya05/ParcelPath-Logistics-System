from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class NotificationType(models.TextChoices):
    INFO = "INFO", "Information"
    SUCCESS = "SUCCESS", "Success"
    WARNING = "WARNING", "Warning"
    ERROR = "ERROR", "Error"
    SHIPMENT = "SHIPMENT", "Shipment"
    DELIVERY = "DELIVERY", "Delivery"


class Notification(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    title = models.CharField(
        max_length=200,
    )

    message = models.TextField()

    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.INFO,
        db_index=True,
    )

    is_read = models.BooleanField(
        default=False,
        db_index=True,
    )

    action_url = models.CharField(
        max_length=300,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    read_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:

        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

        ordering = [
            "-created_at",
        ]

        indexes = [
            models.Index(
                fields=[
                    "user",
                    "is_read",
                ]
            ),
            models.Index(
                fields=[
                    "user",
                    "-created_at",
                ]
            ),
            models.Index(
                fields=[
                    "notification_type",
                ]
            ),
        ]

    def __str__(self):
        return (
            f"{self.user.email} - {self.title}"
        )

    @property
    def is_unread(self):
        return not self.is_read

    @property
    def has_action(self):
        return bool(self.action_url)

    @property
    def icon(self):
        icons = {
            NotificationType.INFO: "bi-info-circle",
            NotificationType.SUCCESS: "bi-check-circle",
            NotificationType.WARNING: "bi-exclamation-triangle",
            NotificationType.ERROR: "bi-x-circle",
            NotificationType.SHIPMENT: "bi-box-seam",
            NotificationType.DELIVERY: "bi-truck",
        }

        return icons.get(
            self.notification_type,
            "bi-bell",
        )

    @property
    def badge_class(self):
        badges = {
            NotificationType.INFO: "primary",
            NotificationType.SUCCESS: "success",
            NotificationType.WARNING: "warning",
            NotificationType.ERROR: "danger",
            NotificationType.SHIPMENT: "info",
            NotificationType.DELIVERY: "success",
        }

        return badges.get(
            self.notification_type,
            "secondary",
        )

    def mark_as_read(self):

        if self.is_read:
            return

        self.is_read = True
        self.read_at = timezone.now()

        self.save(
            update_fields=[
                "is_read",
                "read_at",
            ]
        )

    def mark_as_unread(self):

        self.is_read = False
        self.read_at = None

        self.save(
            update_fields=[
                "is_read",
                "read_at",
            ]
        )

    def get_absolute_url(self):

        if self.action_url:
            return self.action_url

        return reverse(
            "notifications:notification_list",
        )

    @classmethod
    def create_notification(
        cls,
        *,
        user,
        title,
        message,
        notification_type=NotificationType.INFO,
        action_url="",
    ):
        return cls.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            action_url=action_url,
        )

    @classmethod
    def unread_count(
        cls,
        user,
    ):
        return cls.objects.filter(
            user=user,
            is_read=False,
        ).count()

    @classmethod
    def mark_all_as_read(
        cls,
        user,
    ):
        return cls.objects.filter(
            user=user,
            is_read=False,
        ).update(
            is_read=True,
            read_at=timezone.now(),
        )

    @classmethod
    def delete_old_notifications(
        cls,
        days=90,
    ):
        cutoff = timezone.now() - timezone.timedelta(days=days)

        return cls.objects.filter(
            created_at__lt=cutoff,
        ).delete()