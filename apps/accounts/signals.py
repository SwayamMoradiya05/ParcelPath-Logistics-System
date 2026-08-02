from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.accounts.models import User, UserRole
from apps.customers.models import Customer


@receiver(post_save, sender=User)
def create_customer_profile(sender, instance, created, **kwargs):
    print("=" * 60)
    print("SIGNAL FIRED")
    print("Created:", created)
    print("Role:", instance.role)

    if created and instance.role == UserRole.CUSTOMER:
        print("Creating customer...")

        customer = Customer.objects.create(
            user=instance,
            address_line_1="Pending",
            city="Pending",
            state="Pending",
            postal_code="000000",
        )

        print("Customer created:", customer.customer_id)