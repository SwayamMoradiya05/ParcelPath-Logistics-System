import uuid

from django.core.validators import MinValueValidator
from django.db import models

from apps.drivers.models import Driver
from apps.shipments.models import Shipment


class RouteStatus(models.TextChoices):
    PLANNED = "PLANNED", "Planned"
    ASSIGNED = "ASSIGNED", "Assigned"
    STARTED = "STARTED", "Started"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"


class Route(models.Model):
    route_code = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        db_index=True,
    )

    name = models.CharField(
        max_length=150,
        db_index=True,
    )

    driver = models.ForeignKey(
        Driver,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="routes",
    )

    origin = models.CharField(
        max_length=200,
        db_index=True,
    )

    destination = models.CharField(
        max_length=200,
        db_index=True,
    )

    total_distance = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(0),
        ],
    )

    estimated_duration = models.PositiveIntegerField(
        help_text="Duration in minutes",
        default=0,
    )

    status = models.CharField(
        max_length=20,
        choices=RouteStatus.choices,
        default=RouteStatus.PLANNED,
        db_index=True,
    )

    notes = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        verbose_name = "Route"
        verbose_name_plural = "Routes"

        ordering = [
            "-created_at",
        ]

        indexes = [
            models.Index(fields=["route_code"]),
            models.Index(fields=["driver"]),
            models.Index(fields=["status"]),
            models.Index(fields=["origin"]),
            models.Index(fields=["destination"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.route_code} - {self.name}"

    def save(self, *args, **kwargs):
        self.name = self.name.strip().title()
        self.origin = self.origin.strip().title()
        self.destination = self.destination.strip().title()

        if not self.route_code:
            while True:
                code = (
                    f"RTE-{uuid.uuid4().hex[:8].upper()}"
                )

                if not Route.objects.filter(
                    route_code=code
                ).exists():
                    self.route_code = code
                    break

        super().save(*args, **kwargs)

    @property
    def total_shipments(self):
        return self.route_shipments.count()

    @property
    def delivered_shipments(self):
        return self.route_shipments.filter(
            delivered=True
        ).count()

    @property
    def pending_shipments(self):
        return (
            self.total_shipments
            - self.delivered_shipments
        )

    @property
    def completion_percentage(self):
        total = self.total_shipments

        if total == 0:
            return 0

        return round(
            (self.delivered_shipments / total) * 100,
            2,
        )

    @property
    def is_completed(self):
        return (
            self.status == RouteStatus.COMPLETED
        )

    def assign_driver(self, driver):
        self.driver = driver
        self.status = RouteStatus.ASSIGNED

        self.save(
            update_fields=[
                "driver",
                "status",
            ]
        )

    def start_route(self):
        self.status = RouteStatus.STARTED

        self.save(
            update_fields=[
                "status",
            ]
        )

    def complete_route(self):
        self.status = RouteStatus.COMPLETED

        self.save(
            update_fields=[
                "status",
            ]
        )

    def cancel_route(self):
        self.status = RouteStatus.CANCELLED

        self.save(
            update_fields=[
                "status",
            ]
        )


class RouteShipment(models.Model):
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="route_shipments",
    )

    shipment = models.OneToOneField(
        Shipment,
        on_delete=models.CASCADE,
        related_name="route_assignment",
    )

    stop_number = models.PositiveIntegerField()

    delivered = models.BooleanField(
        default=False,
        db_index=True,
    )

    class Meta:
        verbose_name = "Route Shipment"
        verbose_name_plural = "Route Shipments"

        ordering = [
            "stop_number",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "route",
                    "stop_number",
                ],
                name="unique_route_stop",
            ),
        ]

        indexes = [
            models.Index(fields=["route"]),
            models.Index(fields=["shipment"]),
            models.Index(fields=["stop_number"]),
            models.Index(fields=["delivered"]),
        ]

    def __str__(self):
        return (
            f"{self.route.route_code} "
            f"- Stop {self.stop_number}"
        )

    def mark_delivered(self):
        self.delivered = True

        self.save(
            update_fields=[
                "delivered",
            ]
        )