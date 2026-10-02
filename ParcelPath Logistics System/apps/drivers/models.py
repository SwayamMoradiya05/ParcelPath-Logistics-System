from datetime import date

from django.conf import settings
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    RegexValidator,
)
from django.db import models


class Driver(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Available"
        ON_DELIVERY = "ON_DELIVERY", "On Delivery"
        OFF_DUTY = "OFF_DUTY", "Off Duty"
        ON_LEAVE = "ON_LEAVE", "On Leave"

    class VehicleType(models.TextChoices):
        BIKE = "BIKE", "Bike"
        VAN = "VAN", "Van"
        MINI_TRUCK = "MINI_TRUCK", "Mini Truck"
        TRUCK = "TRUCK", "Truck"

    driver_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        db_index=True,
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="driver_profile",
    )

    license_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
    )

    license_expiry = models.DateField()

    vehicle_type = models.CharField(
        max_length=20,
        choices=VehicleType.choices,
        db_index=True,
    )

    vehicle_number = models.CharField(
        max_length=30,
        unique=True,
        db_index=True,
    )

    vehicle_model = models.CharField(
        max_length=100,
    )

    vehicle_capacity = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
        ],
        help_text="Capacity in KG",
    )

    alternate_phone = models.CharField(
        max_length=15,
        blank=True,
        validators=[
            RegexValidator(
                regex=r"^\+?[0-9]{10,15}$",
                message="Enter a valid phone number.",
            )
        ],
    )

    profile_image = models.ImageField(
        upload_to="drivers/",
        blank=True,
        null=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE,
        db_index=True,
    )

    current_latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        blank=True,
        null=True,
    )

    current_longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        blank=True,
        null=True,
    )

    total_deliveries = models.PositiveIntegerField(
        default=0,
    )

    successful_deliveries = models.PositiveIntegerField(
        default=0,
    )

    cancelled_deliveries = models.PositiveIntegerField(
        default=0,
    )

    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=5.00,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5),
        ],
    )

    is_verified = models.BooleanField(
        default=False,
    )

    joined_date = models.DateField(
        auto_now_add=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        verbose_name = "Driver"
        verbose_name_plural = "Drivers"

        ordering = [
            "user__first_name",
            "user__last_name",
        ]

        indexes = [
            models.Index(fields=["driver_id"]),
            models.Index(fields=["status"]),
            models.Index(fields=["vehicle_type"]),
            models.Index(fields=["license_number"]),
            models.Index(fields=["vehicle_number"]),
            models.Index(fields=["is_verified"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return self.user.full_name or self.user.email

    def save(self, *args, **kwargs):
        if self.alternate_phone:
            self.alternate_phone = self.alternate_phone.strip()

        if self.vehicle_number:
            self.vehicle_number = self.vehicle_number.upper().strip()

        if self.license_number:
            self.license_number = self.license_number.upper().strip()

        if not self.driver_id:
            last_driver = (
                Driver.objects.order_by("-id")
                .only("id")
                .first()
            )

            next_id = (
                last_driver.id + 1
                if last_driver
                else 1
            )

            self.driver_id = f"DRV{next_id:06d}"

        super().save(*args, **kwargs)

    @property
    def availability(self):
        return self.status == self.Status.AVAILABLE

    @property
    def is_available(self):
        return self.status == self.Status.AVAILABLE

    @property
    def completion_rate(self):
        if self.total_deliveries == 0:
            return 0

        return round(
            (
                self.successful_deliveries
                / self.total_deliveries
            )
            * 100,
            2,
        )

    @property
    def pending_deliveries(self):
        return (
            self.total_deliveries
            - self.successful_deliveries
            - self.cancelled_deliveries
        )

    @property
    def is_license_expired(self):
        return self.license_expiry < date.today()

    @property
    def days_until_license_expiry(self):
        return (
            self.license_expiry
            - date.today()
        ).days

    def verify(self):
        self.is_verified = True
        self.save(
            update_fields=[
                "is_verified",
            ]
        )

    def unverify(self):
        self.is_verified = False
        self.save(
            update_fields=[
                "is_verified",
            ]
        )

    def set_available(self):
        self.status = self.Status.AVAILABLE
        self.save(
            update_fields=[
                "status",
            ]
        )

    def set_on_delivery(self):
        self.status = self.Status.ON_DELIVERY
        self.save(
            update_fields=[
                "status",
            ]
        )

    def set_off_duty(self):
        self.status = self.Status.OFF_DUTY
        self.save(
            update_fields=[
                "status",
            ]
        )

    def set_on_leave(self):
        self.status = self.Status.ON_LEAVE
        self.save(
            update_fields=[
                "status",
            ]
        )

    def update_location(
        self,
        latitude,
        longitude,
    ):
        self.current_latitude = latitude
        self.current_longitude = longitude

        self.save(
            update_fields=[
                "current_latitude",
                "current_longitude",
            ]
        )

    def increment_successful_delivery(self):
        self.total_deliveries += 1
        self.successful_deliveries += 1

        self.save(
            update_fields=[
                "total_deliveries",
                "successful_deliveries",
            ]
        )

    def increment_cancelled_delivery(self):
        self.total_deliveries += 1
        self.cancelled_deliveries += 1

        self.save(
            update_fields=[
                "total_deliveries",
                "cancelled_deliveries",
            ]
        )