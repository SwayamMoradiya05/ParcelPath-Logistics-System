from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.shipments.models import Shipment


class TrackingStatus(models.TextChoices):
    CREATED = "CREATED", "Created"
    PICKUP_ASSIGNED = "PICKUP_ASSIGNED", "Pickup Assigned"
    PICKED_UP = "PICKED_UP", "Picked Up"
    IN_TRANSIT = "IN_TRANSIT", "In Transit"
    ARRIVED_AT_HUB = "ARRIVED_AT_HUB", "Arrived At Hub"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY", "Out For Delivery"
    DELIVERED = "DELIVERED", "Delivered"
    CANCELLED = "CANCELLED", "Cancelled"
    RETURNED = "RETURNED", "Returned"


class TrackingEvent(models.Model):

    shipment = models.ForeignKey(
        Shipment,
        on_delete=models.CASCADE,
        related_name="tracking_events",
    )

    status = models.CharField(
        max_length=30,
        choices=TrackingStatus.choices,
        db_index=True,
    )

    location = models.CharField(
        max_length=255,
        db_index=True,
    )

    description = models.TextField()

    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(-90),
            MaxValueValidator(90),
        ],
    )

    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(-180),
            MaxValueValidator(180),
        ],
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tracking_updates",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Tracking Event"
        verbose_name_plural = "Tracking Events"

        ordering = [
            "created_at",
        ]

        indexes = [
            models.Index(fields=["shipment"]),
            models.Index(fields=["status"]),
            models.Index(fields=["location"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["shipment", "created_at"]),
        ]

    def __str__(self):
        return (
            f"{self.shipment.tracking_number}"
            f" - {self.get_status_display()}"
        )

    @property
    def has_coordinates(self):
        return (
            self.latitude is not None
            and self.longitude is not None
        )

    @property
    def coordinates(self):
        if self.has_coordinates:
            return (
                float(self.latitude),
                float(self.longitude),
            )
        return None

    @property
    def google_maps_url(self):
        if self.has_coordinates:
            return (
                f"https://maps.google.com/?q="
                f"{self.latitude},{self.longitude}"
            )
        return None

    @property
    def is_final_status(self):
        return self.status in (
            TrackingStatus.DELIVERED,
            TrackingStatus.CANCELLED,
            TrackingStatus.RETURNED,
        )

    @classmethod
    def create_event(
        cls,
        shipment,
        status,
        location,
        description,
        user=None,
        latitude=None,
        longitude=None,
    ):
        return cls.objects.create(
            shipment=shipment,
            status=status,
            location=location,
            description=description,
            updated_by=user,
            latitude=latitude,
            longitude=longitude,
        )

    def update_location(
        self,
        latitude,
        longitude,
    ):
        self.latitude = latitude
        self.longitude = longitude

        self.save(
            update_fields=[
                "latitude",
                "longitude",
            ]
        )

    def mark_delivered(self):
        self.status = TrackingStatus.DELIVERED

        self.save(
            update_fields=[
                "status",
            ]
        )

    def mark_cancelled(self):
        self.status = TrackingStatus.CANCELLED

        self.save(
            update_fields=[
                "status",
            ]
        )

    def mark_returned(self):
        self.status = TrackingStatus.RETURNED

        self.save(
            update_fields=[
                "status",
            ]
        )