from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.accounts.models import User, UserRole

from .models import Driver


@receiver(post_save, sender=User)
def create_driver_profile(sender, instance, created, **kwargs):
    if (
        created
        and instance.role == UserRole.DRIVER
        and not hasattr(instance, "driver_profile")
    ):
        # Driver profile should be completed later by the driver/admin.
        Driver.objects.create(
            user=instance,
            license_number=f"TEMP-{instance.id}",
            license_expiry="2099-12-31",
            vehicle_type=Driver.VehicleType.BIKE,
            vehicle_number=f"TEMP-{instance.id}",
            vehicle_model="Not Assigned",
            vehicle_capacity=1,
        )