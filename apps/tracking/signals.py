from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.shipments.models import Shipment
from apps.shipments.models import ShipmentStatus

from .models import TrackingEvent
from .models import TrackingStatus


STATUS_MAPPING = {
    ShipmentStatus.PENDING: TrackingStatus.CREATED,
    ShipmentStatus.PICKUP_ASSIGNED: TrackingStatus.PICKUP_ASSIGNED,
    ShipmentStatus.PICKED_UP: TrackingStatus.PICKED_UP,
    ShipmentStatus.IN_TRANSIT: TrackingStatus.IN_TRANSIT,
    ShipmentStatus.OUT_FOR_DELIVERY: TrackingStatus.OUT_FOR_DELIVERY,
    ShipmentStatus.DELIVERED: TrackingStatus.DELIVERED,
    ShipmentStatus.CANCELLED: TrackingStatus.CANCELLED,
    ShipmentStatus.RETURNED: TrackingStatus.RETURNED,
}


@receiver(post_save, sender=Shipment)
def create_initial_tracking(sender, instance, created, **kwargs):
    if not created:
        return

    TrackingEvent.objects.create(
        shipment=instance,
        status=TrackingStatus.CREATED,
        location="Shipment Created",
        description="Shipment has been created.",
    )


@receiver(post_save, sender=Shipment)
def sync_tracking_status(sender, instance, created, **kwargs):
    if created:
        return

    tracking_status = STATUS_MAPPING.get(instance.status)

    if not tracking_status:
        return

    last_event = (
        instance.tracking_events.order_by("-created_at").first()
    )

    if (
        last_event
        and last_event.status == tracking_status
    ):
        return

    TrackingEvent.objects.create(
        shipment=instance,
        status=tracking_status,
        location="System Update",
        description=f"Shipment status changed to {instance.get_status_display()}.",
    )