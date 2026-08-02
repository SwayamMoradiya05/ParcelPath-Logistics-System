from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.shipments.models import Shipment
from apps.shipments.models import ShipmentStatus

from .models import NotificationType
from .services import NotificationService


@receiver(post_save, sender=Shipment)
def shipment_notification(
    sender,
    instance,
    created,
    **kwargs,
):
    customer = instance.customer.user

    if created:
        NotificationService.create(
            user=customer,
            title="Shipment Created",
            message=(
                f"Shipment {instance.tracking_number} "
                "has been created successfully."
            ),
            notification_type=NotificationType.SHIPMENT,
            action_url=f"/shipments/{instance.pk}/",
        )

        return

    status_messages = {
        ShipmentStatus.PICKUP_ASSIGNED:
            "Pickup has been assigned.",
        ShipmentStatus.PICKED_UP:
            "Shipment has been picked up.",
        ShipmentStatus.IN_TRANSIT:
            "Shipment is in transit.",
        ShipmentStatus.OUT_FOR_DELIVERY:
            "Shipment is out for delivery.",
        ShipmentStatus.DELIVERED:
            "Shipment has been delivered.",
        ShipmentStatus.CANCELLED:
            "Shipment has been cancelled.",
        ShipmentStatus.RETURNED:
            "Shipment has been returned.",
    }

    if instance.status in status_messages:
        NotificationService.create(
            user=customer,
            title=instance.get_status_display(),
            message=status_messages[instance.status],
            notification_type=NotificationType.SHIPMENT,
            action_url=f"/shipments/{instance.pk}/",
        )