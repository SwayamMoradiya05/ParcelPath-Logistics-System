from django.db import transaction
from django.db.models import Count, Sum

from apps.drivers.models import Driver
from apps.shipments.models import ShipmentStatus

from .models import Route, RouteShipment, RouteStatus


class RouteService:
    @staticmethod
    def dashboard_statistics():
        return {
            "total_routes": Route.objects.count(),
            "planned_routes": Route.objects.filter(
                status=RouteStatus.PLANNED,
            ).count(),
            "assigned_routes": Route.objects.filter(
                status=RouteStatus.ASSIGNED,
            ).count(),
            "active_routes": Route.objects.filter(
                status=RouteStatus.STARTED,
            ).count(),
            "completed_routes": Route.objects.filter(
                status=RouteStatus.COMPLETED,
            ).count(),
            "cancelled_routes": Route.objects.filter(
                status=RouteStatus.CANCELLED,
            ).count(),
            "total_distance": Route.objects.aggregate(
                total=Sum("total_distance"),
            )["total"] or 0,
            "total_shipments": RouteShipment.objects.count(),
        }

    @staticmethod
    def get_all():
        return (
            Route.objects.select_related(
                "driver",
                "driver__user",
            )
            .prefetch_related(
                "route_shipments__shipment",
            )
            .order_by("-created_at")
        )

    @staticmethod
    def get_by_id(route_id):
        return (
            Route.objects.select_related(
                "driver",
                "driver__user",
            )
            .prefetch_related(
                "route_shipments__shipment",
            )
            .get(pk=route_id)
        )

    @staticmethod
    @transaction.atomic
    def assign_driver(route, driver):
        route.assign_driver(driver)

    @staticmethod
    @transaction.atomic
    def add_shipment(route, shipment):
        stop_number = (
            RouteShipment.objects.filter(
                route=route,
            ).count()
            + 1
        )

        RouteShipment.objects.create(
            route=route,
            shipment=shipment,
            stop_number=stop_number,
        )

        shipment.status = ShipmentStatus.PICKUP_ASSIGNED
        shipment.save(
            update_fields=[
                "status",
            ]
        )

    @staticmethod
    @transaction.atomic
    def remove_shipment(route, shipment):
        RouteShipment.objects.filter(
            route=route,
            shipment=shipment,
        ).delete()

        remaining = (
            RouteShipment.objects.filter(
                route=route,
            )
            .order_by("stop_number")
        )

        for index, item in enumerate(remaining, start=1):
            if item.stop_number != index:
                item.stop_number = index
                item.save(
                    update_fields=[
                        "stop_number",
                    ]
                )

    @staticmethod
    @transaction.atomic
    def start_route(route):
        route.start_route()

    @staticmethod
    @transaction.atomic
    def complete_route(route):
        route.complete_route()

    @staticmethod
    @transaction.atomic
    def cancel_route(route):
        route.cancel_route()

    @staticmethod
    def routes_by_status(status):
        return (
            Route.objects.filter(
                status=status,
            )
            .select_related(
                "driver",
                "driver__user",
            )
            .order_by("-created_at")
        )

    @staticmethod
    def routes_by_driver(driver):
        return (
            Route.objects.filter(
                driver=driver,
            )
            .prefetch_related(
                "route_shipments__shipment",
            )
            .order_by("-created_at")
        )

    @staticmethod
    def unassigned_routes():
        return (
            Route.objects.filter(
                driver__isnull=True,
            )
            .order_by("-created_at")
        )

    @staticmethod
    def route_statistics(route):
        return {
            "total_shipments": route.total_shipments,
            "delivered_shipments": route.delivered_shipments,
            "pending_shipments": route.pending_shipments,
            "completion_percentage": route.completion_percentage,
        }

    @staticmethod
    def top_drivers(limit=5):
        return (
            Driver.objects.annotate(
                completed_routes=Count(
                    "routes",
                ),
            )
            .order_by("-completed_routes")[:limit]
        )