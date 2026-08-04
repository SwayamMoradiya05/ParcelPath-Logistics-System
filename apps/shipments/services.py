from django.db import transaction
from django.db.models import Count, Q, Sum
from django.utils import timezone

from apps.drivers.models import Driver
from apps.notifications.services import NotificationService
from .models import Shipment, ShipmentStatus


class ShipmentService:

    @staticmethod
    def get_all():
        return (
            Shipment.objects.select_related(
                "customer",
                "driver",
                "created_by",
            )
            .order_by("-created_at")
        )

    @staticmethod
    def get_by_tracking_number(tracking_number):
        return (
            Shipment.objects.select_related(
                "customer",
                "driver",
                "created_by",
            )
            .filter(
                tracking_number=tracking_number,
            )
            .first()
        )

    @staticmethod
    def dashboard_statistics():
        queryset = Shipment.objects.all()

        return {
            "total_shipments": queryset.count(),
            "pending": queryset.filter(
                status=ShipmentStatus.PENDING
            ).count(),
            "pickup_assigned": queryset.filter(
                status=ShipmentStatus.PICKUP_ASSIGNED
            ).count(),
            "picked_up": queryset.filter(
                status=ShipmentStatus.PICKED_UP
            ).count(),
            "transit": queryset.filter(
                status=ShipmentStatus.IN_TRANSIT
            ).count(),
            "out_for_delivery": queryset.filter(
                status=ShipmentStatus.OUT_FOR_DELIVERY
            ).count(),
            "delivered": queryset.filter(
                status=ShipmentStatus.DELIVERED
            ).count(),
            "cancelled": queryset.filter(
                status=ShipmentStatus.CANCELLED
            ).count(),
            "returned": queryset.filter(
                status=ShipmentStatus.RETURNED
            ).count(),
            "active": queryset.exclude(
                status__in=[
                    ShipmentStatus.DELIVERED,
                    ShipmentStatus.CANCELLED,
                    ShipmentStatus.RETURNED,
                ]
            ).count(),
            "total_revenue": queryset.aggregate(
                revenue=Sum("shipping_cost")
            )["revenue"]
            or 0,
        }

    @staticmethod
    
    @transaction.atomic
    def assign_driver(shipment, driver):
        """
        Assign a verified and available driver to a shipment.
        """

        if driver.status != Driver.Status.AVAILABLE:
            raise ValueError("Selected driver is not available.")

        if not driver.is_verified:
            raise ValueError("Selected driver is not verified.")

        shipment.assign_driver(driver)

        return shipment

    @staticmethod
    @transaction.atomic
    def update_status(shipment, status):

        if not shipment.can_change_to(status):
            raise ValueError(
                f"Cannot change shipment status from "
                f"{shipment.get_status_display()} "
                f"to {status}."
            )

        old_status = shipment.status

        mapping = {
            ShipmentStatus.PICKED_UP: shipment.mark_picked_up,
            ShipmentStatus.IN_TRANSIT: shipment.mark_in_transit,
            ShipmentStatus.OUT_FOR_DELIVERY: shipment.mark_out_for_delivery,
            ShipmentStatus.DELIVERED: shipment.mark_delivered,
            ShipmentStatus.CANCELLED: shipment.mark_cancelled,
            ShipmentStatus.RETURNED: shipment.mark_returned,
        }

        action = mapping.get(status)

        if action is None:
            raise ValueError("Invalid shipment status.")

        action()

        # Send SMS ONLY when status changes to DELIVERED
        if (
            old_status != ShipmentStatus.DELIVERED
            and shipment.status == ShipmentStatus.DELIVERED
        ):
            NotificationService.delivery_completed(
                shipment.customer,
                shipment,
            )

        return shipment


    @staticmethod
    def search(query):
        return (
            Shipment.objects.select_related(
                "customer",
                "driver",
                "created_by",
            )
            .filter(
                Q(tracking_number__icontains=query)
                | Q(sender_name__icontains=query)
                | Q(receiver_name__icontains=query)
                | Q(sender_phone__icontains=query)
                | Q(receiver_phone__icontains=query)
            )
            .order_by("-created_at")
        )

    @staticmethod
    def recent_shipments(limit=10):
        return (
            Shipment.objects.select_related(
                "customer",
                "driver",
                "created_by",
            )
            .order_by("-created_at")[:limit]
        )

    @staticmethod
    def shipments_by_status(status):
        return (
            Shipment.objects.select_related(
                "customer",
                "driver",
            )
            .filter(
                status=status,
            )
        )

    @staticmethod
    def revenue_summary():
        return Shipment.objects.aggregate(
            total_shipments=Count("id"),
            total_revenue=Sum("shipping_cost"),
            total_declared_value=Sum("declared_value"),
        )

    @staticmethod
    def overdue_shipments():
        today = timezone.now().date()

        return (
            Shipment.objects.select_related(
                "customer",
                "driver",
            )
            .filter(
                expected_delivery__lt=today,
            )
            .exclude(
                status=ShipmentStatus.DELIVERED,
            )
        )

    @staticmethod
    def unassigned_shipments():
        return (
            Shipment.objects.select_related(
                "customer",
            )
            .filter(
                driver__isnull=True,
            )
        )