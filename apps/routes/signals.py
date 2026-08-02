from django.db.models.signals import post_delete
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import RouteShipment
from .utils import optimize_stop_numbers


@receiver(post_save, sender=RouteShipment)
def reorder_after_create(
    sender,
    instance,
    created,
    **kwargs,
):
    if created:
        optimize_stop_numbers(instance.route)


@receiver(post_delete, sender=RouteShipment)
def reorder_after_delete(
    sender,
    instance,
    **kwargs,
):
    optimize_stop_numbers(instance.route)