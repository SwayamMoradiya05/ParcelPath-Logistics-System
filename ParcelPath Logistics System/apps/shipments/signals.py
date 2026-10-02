from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.customers.models import Customer

from .models import Shipment, ShipmentStatus


@receiver(post_save, sender=Shipment)
def update_customer_statistics(
    sender,
    instance,
    created,
    **kwargs,
):
    customer = instance.customer

    if created:
        customer.total_shipments += 1

    if instance.status == ShipmentStatus.DELIVERED:
        customer.completed_shipments = Shipment.objects.filter(
            customer=customer,
            status=ShipmentStatus.DELIVERED,
        ).count()

    if instance.status == ShipmentStatus.CANCELLED:
        customer.cancelled_shipments = Shipment.objects.filter(
            customer=customer,
            status=ShipmentStatus.CANCELLED,
        ).count()

    customer.save(
        update_fields=[
            "total_shipments",
            "completed_shipments",
            "cancelled_shipments",
        ]
    )