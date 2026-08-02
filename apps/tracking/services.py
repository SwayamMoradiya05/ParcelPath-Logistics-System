from django.db import transaction

from apps.shipments.models import ShipmentStatus

from .models import TrackingEvent, TrackingStatus


class TrackingService:

    @staticmethod
    @transaction.atomic
    def create_event(
        shipment,
        status,
        description,
        location,
        latitude=None,
        longitude=None,
        user=None,
    ):
        event = TrackingEvent.objects.create(
            shipment=shipment,
            status=status,
            description=description.strip(),
            location=location.strip().title(),
            latitude=latitude or None,
            longitude=longitude or None,
            updated_by=user,
        )

        TrackingService.update_shipment_status(
            shipment,
            status,
        )

        return event

    @staticmethod
    @transaction.atomic
    def update_shipment_status(
        shipment,
        tracking_status,
    ):
        status_map = {
            TrackingStatus.CREATED:
                ShipmentStatus.PENDING,

            TrackingStatus.PICKUP_ASSIGNED:
                ShipmentStatus.PICKUP_ASSIGNED,

            TrackingStatus.PICKED_UP:
                ShipmentStatus.PICKED_UP,

            TrackingStatus.IN_TRANSIT:
                ShipmentStatus.IN_TRANSIT,

            TrackingStatus.ARRIVED_AT_HUB:
                ShipmentStatus.IN_TRANSIT,

            TrackingStatus.OUT_FOR_DELIVERY:
                ShipmentStatus.OUT_FOR_DELIVERY,

            TrackingStatus.DELIVERED:
                ShipmentStatus.DELIVERED,

            TrackingStatus.CANCELLED:
                ShipmentStatus.CANCELLED,

            TrackingStatus.RETURNED:
                ShipmentStatus.RETURNED,
        }

        shipment_status = status_map.get(
            tracking_status
        )

        if shipment_status:
            shipment.status = shipment_status

            if shipment_status == ShipmentStatus.DELIVERED:
                shipment.mark_delivered()

            elif shipment_status == ShipmentStatus.CANCELLED:
                shipment.mark_cancelled()

            elif shipment_status == ShipmentStatus.RETURNED:
                shipment.mark_returned()

            elif shipment_status == ShipmentStatus.PICKED_UP:
                shipment.mark_picked_up()

            elif shipment_status == ShipmentStatus.IN_TRANSIT:
                shipment.mark_in_transit()

            elif shipment_status == ShipmentStatus.OUT_FOR_DELIVERY:
                shipment.mark_out_for_delivery()

            elif shipment_status == ShipmentStatus.PICKUP_ASSIGNED:
                shipment.save(
                    update_fields=[
                        "status",
                    ]
                )

    @staticmethod
    def latest_event(shipment):
        return (
            shipment.tracking_events
            .select_related(
                "updated_by",
            )
            .order_by("-created_at")
            .first()
        )

    @staticmethod
    def history(shipment):
        return (
            shipment.tracking_events
            .select_related(
                "updated_by",
            )
            .order_by("created_at")
        )

    @staticmethod
    def recent_events(limit=10):
        return (
            TrackingEvent.objects.select_related(
                "shipment",
                "updated_by",
            )
            .order_by("-created_at")[:limit]
        )

    @staticmethod
    def events_by_status(status):
        return (
            TrackingEvent.objects.select_related(
                "shipment",
                "updated_by",
            )
            .filter(
                status=status,
            )
            .order_by("-created_at")
        )

    @staticmethod
    def shipment_history(tracking_number):
        return (
            TrackingEvent.objects.select_related(
                "shipment",
                "updated_by",
            )
            .filter(
                shipment__tracking_number=tracking_number,
            )
            .order_by("created_at")
        )