import logging

from django.db import transaction
from django.urls import reverse

from apps.notifications.sms_service import SMSService

from .models import Notification, NotificationType

logger = logging.getLogger(__name__)


class NotificationService:

    @staticmethod
    @transaction.atomic
    def create(
        user,
        title,
        message,
        notification_type=NotificationType.INFO,
        action_url="",
    ):
        return Notification.objects.create(
            user=user,
            title=title.strip(),
            message=message.strip(),
            notification_type=notification_type,
            action_url=action_url,
        )

    @staticmethod
    def shipment_created(user, shipment):
        return NotificationService.create(
            user=user,
            title="Shipment Created",
            message=f"Shipment {shipment.tracking_number} has been created successfully.",
            notification_type=NotificationType.SHIPMENT,
            action_url=reverse(
                "shipments:shipment_detail",
                args=[shipment.pk],
            ),
        )

    @staticmethod
    def shipment_delivered(user, shipment):
        return NotificationService.create(
            user=user,
            title="Shipment Delivered",
            message=f"Shipment {shipment.tracking_number} has been delivered successfully.",
            notification_type=NotificationType.SUCCESS,
            action_url=reverse(
                "shipments:shipment_detail",
                args=[shipment.pk],
            ),
        )

    @staticmethod
    def shipment_cancelled(user, shipment):
        return NotificationService.create(
            user=user,
            title="Shipment Cancelled",
            message=f"Shipment {shipment.tracking_number} has been cancelled.",
            notification_type=NotificationType.WARNING,
            action_url=reverse(
                "shipments:shipment_detail",
                args=[shipment.pk],
            ),
        )

    @staticmethod
    def delivery_assigned(user, shipment):
        return NotificationService.create(
            user=user,
            title="Driver Assigned",
            message=f"A driver has been assigned to shipment {shipment.tracking_number}.",
            notification_type=NotificationType.DELIVERY,
            action_url=reverse(
                "shipments:shipment_detail",
                args=[shipment.pk],
            ),
        )

    @staticmethod
    def custom_notification(
        user,
        title,
        message,
        notification_type=NotificationType.INFO,
        action_url="",
    ):
        return NotificationService.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            action_url=action_url,
        )

    @staticmethod
    def delivery_completed(customer, shipment):
        phone = customer.user.phone

        if not phone:
            return

        message = (
            f"ParcelPath Logistics\n\n"
            f"Hello {customer.user.first_name},\n\n"
            f"Your parcel ({shipment.tracking_number}) "
            f"has been delivered successfully.\n\n"
            f"Thank you for choosing ParcelPath."
        )

        try:
            SMSService.send(
                phone_number=phone,
                message=message,
            )
        except Exception:
            logger.exception("SMS sending failed.")

    @staticmethod
    def unread_count(user):
        return Notification.unread_count(user)

    @staticmethod
    def mark_all_as_read(user):
        return Notification.mark_all_as_read(user)

    @staticmethod
    def delete_notification(notification):
        notification.delete()

    @staticmethod
    def latest_notifications(user, limit=10):
        return (
            Notification.objects.filter(
                user=user,
            )
            .order_by("-created_at")[:limit]
        )

    @staticmethod
    def unread_notifications(user):
        return (
            Notification.objects.filter(
                user=user,
                is_read=False,
            )
            .order_by("-created_at")
        )