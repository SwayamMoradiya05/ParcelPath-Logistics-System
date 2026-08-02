from django.db.models import Count
from django.db.models import Sum

from apps.customers.models import Customer
from apps.drivers.models import Driver
from apps.routes.models import Route
from apps.shipments.models import Shipment
from apps.shipments.models import ShipmentStatus


class DashboardService:

    @staticmethod
    def shipment_statistics():
        return {
            "total": Shipment.objects.count(),
            "pending": Shipment.objects.filter(
                status=ShipmentStatus.PENDING
            ).count(),
            "assigned": Shipment.objects.filter(
                status=ShipmentStatus.PICKUP_ASSIGNED
            ).count(),
            "picked": Shipment.objects.filter(
                status=ShipmentStatus.PICKED_UP
            ).count(),
            "transit": Shipment.objects.filter(
                status=ShipmentStatus.IN_TRANSIT
            ).count(),
            "delivery": Shipment.objects.filter(
                status=ShipmentStatus.OUT_FOR_DELIVERY
            ).count(),
            "delivered": Shipment.objects.filter(
                status=ShipmentStatus.DELIVERED
            ).count(),
            "cancelled": Shipment.objects.filter(
                status=ShipmentStatus.CANCELLED
            ).count(),
        }

    @staticmethod
    def revenue():
        return (
            Shipment.objects.aggregate(
                Sum("shipping_cost")
            )["shipping_cost__sum"]
            or 0
        )

    @staticmethod
    def top_drivers(limit=5):
        return (
            Driver.objects.order_by(
                "-successful_deliveries"
            )[:limit]
        )

    @staticmethod
    def top_customers(limit=5):
        return (
            Customer.objects.order_by(
                "-total_shipments"
            )[:limit]
        )

    @staticmethod
    def shipment_status_chart():
        return (
            Shipment.objects.values("status")
            .annotate(total=Count("id"))
            .order_by("status")
        )

    @staticmethod
    def route_statistics():
        return {
            "total": Route.objects.count(),
        }