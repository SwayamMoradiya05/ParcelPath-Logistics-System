import uuid

from django.conf import settings
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone

from apps.customers.models import Customer
from apps.drivers.models import Driver


class ShipmentStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    CONFIRMED = "CONFIRMED", "Confirmed"
    PICKUP_ASSIGNED = "PICKUP_ASSIGNED", "Pickup Assigned"
    PICKED_UP = "PICKED_UP", "Picked Up"
    IN_TRANSIT = "IN_TRANSIT", "In Transit"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY", "Out For Delivery"
    DELIVERED = "DELIVERED", "Delivered"
    CANCELLED = "CANCELLED", "Cancelled"
    RETURNED = "RETURNED", "Returned"


class Shipment(models.Model):
    phone_validator = RegexValidator(
        regex=r"^\+?[0-9]{10,15}$",
        message="Enter a valid phone number.",
    )

    tracking_number = models.CharField(
        max_length=30,
        unique=True,
        editable=False,
        db_index=True,
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="shipments",
    )

    driver = models.ForeignKey(
        Driver,
        on_delete=models.SET_NULL,
        related_name="shipments",
        null=True,
        blank=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_shipments",
    )

    sender_name = models.CharField(
        max_length=120,
    )

    sender_phone = models.CharField(
        max_length=20,
        validators=[phone_validator],
    )

    sender_address = models.TextField()

    receiver_name = models.CharField(
        max_length=120,
    )

    receiver_phone = models.CharField(
        max_length=20,
        validators=[phone_validator],
    )

    receiver_address = models.TextField()

    package_type = models.CharField(
        max_length=100,
        db_index=True,
    )

    weight = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[
            MinValueValidator(0.1),
        ],
    )

    length = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[
            MinValueValidator(0.1),
        ],
    )

    width = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[
            MinValueValidator(0.1),
        ],
    )

    height = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[
            MinValueValidator(0.1),
        ],
    )

    declared_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(0),
        ],
    )

    shipping_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(0),
        ],
    )

    status = models.CharField(
        max_length=30,
        choices=ShipmentStatus.choices,
        default=ShipmentStatus.PENDING,
        db_index=True,
    )

    expected_delivery = models.DateField(
        null=True,
        blank=True,
    )

    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    remarks = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )
    proof_of_delivery = models.ImageField(
    upload_to="proof_of_delivery/",
    blank=True,
    null=True,
    )

    proof_uploaded_at = models.DateTimeField(
        blank=True,
        null=True,
    )
    class Meta:
        verbose_name = "Shipment"
        verbose_name_plural = "Shipments"

        ordering = [
            "-created_at",
        ]

        indexes = [
            models.Index(fields=["tracking_number"]),
            models.Index(fields=["status"]),
            models.Index(fields=["customer"]),
            models.Index(fields=["driver"]),
            models.Index(fields=["package_type"]),
            models.Index(fields=["expected_delivery"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return self.tracking_number

    def save(self, *args, **kwargs):
        self.sender_phone = self.sender_phone.strip()

        self.receiver_phone = self.receiver_phone.strip()

        if not self.tracking_number:
            while True:
                tracking = (
                    f"PP-{uuid.uuid4().hex[:10].upper()}"
                )

                if not Shipment.objects.filter(
                    tracking_number=tracking
                ).exists():
                    self.tracking_number = tracking
                    break

        super().save(*args, **kwargs)

    @property
    def volume(self):
        return (
            self.length
            * self.width
            * self.height
        )

    @property
    def volumetric_weight(self):
        return round(
            self.volume / 5000,
            2,
        )

    @property
    def chargeable_weight(self):
        return max(
            self.weight,
            self.volumetric_weight,
        )

    @property
    def is_delivered(self):
        return (
            self.status
            == ShipmentStatus.DELIVERED
        )

    @property
    def is_cancelled(self):
        return (
            self.status
            == ShipmentStatus.CANCELLED
        )

    @property
    def is_active(self):
        return self.status not in (
            ShipmentStatus.DELIVERED,
            ShipmentStatus.CANCELLED,
            ShipmentStatus.RETURNED,
        )

    def assign_driver(self, driver):
        self.driver = driver
        self.status = ShipmentStatus.PICKUP_ASSIGNED

        driver.status = Driver.Status.ON_DELIVERY
        driver.save(
            update_fields=[
                "status",
            ]
        )

        self.save(
            update_fields=[
                "driver",
                "status",
            ]
        )

    def can_change_to(self, new_status):

        allowed = {

            ShipmentStatus.PENDING: [
                ShipmentStatus.CONFIRMED,
                ShipmentStatus.CANCELLED,
            ],

            ShipmentStatus.CONFIRMED: [
                ShipmentStatus.PICKUP_ASSIGNED,
                ShipmentStatus.CANCELLED,
            ],

            ShipmentStatus.PICKUP_ASSIGNED: [
                ShipmentStatus.PICKED_UP,
            ],

            ShipmentStatus.PICKED_UP: [
                ShipmentStatus.IN_TRANSIT,
            ],

            ShipmentStatus.IN_TRANSIT: [
                ShipmentStatus.OUT_FOR_DELIVERY,
            ],

            ShipmentStatus.OUT_FOR_DELIVERY: [
                ShipmentStatus.DELIVERED,
            ],

            ShipmentStatus.DELIVERED: [
                ShipmentStatus.RETURNED,
            ],

        }

        return new_status in allowed.get(
            self.status,
            [],
        )

    def mark_picked_up(self):
        self.status = ShipmentStatus.PICKED_UP

        self.save(
            update_fields=[
                "status",
            ]
        )

    def mark_in_transit(self):
        self.status = ShipmentStatus.IN_TRANSIT

        self.save(
            update_fields=[
                "status",
            ]
        )

    def mark_out_for_delivery(self):
        self.status = ShipmentStatus.OUT_FOR_DELIVERY

        self.save(
            update_fields=[
                "status",
            ]
        )

    def mark_delivered(self):
        self.status = ShipmentStatus.DELIVERED
        self.delivered_at = timezone.now()

        if self.proof_of_delivery and not self.proof_uploaded_at:
            self.proof_uploaded_at = timezone.now()

        self.save(
            update_fields=[
                "status",
                "delivered_at",
                "proof_uploaded_at",
                "proof_of_delivery",
                "updated_at",
            ]
        )

        # ========================================================
        # SEND DELIVERY EMAIL
        # ========================================================

        try:
            from apps.notifications.email_service import EmailService

            EmailService.send_delivery_confirmation(
                self
            )

        except Exception:
            # Never block successful delivery because
            # email notification failed.
            pass

        # ========================================================
        # SEND SMS
        # ========================================================

        try:
            from apps.notifications.sms_service import SMSService

            phone = self.customer.user.phone

            if phone:
                SMSService.send(
                    phone_number=phone,
                    message=(
                        f"ParcelPath Logistics\n\n"
                        f"Hello "
                        f"{self.customer.user.first_name},\n\n"
                        f"Your parcel "
                        f"({self.tracking_number}) "
                        f"has been delivered successfully.\n\n"
                        f"Thank you for choosing ParcelPath."
                    ),
                )

        except Exception:
            # Never stop delivery because SMS failed.
            pass

        # ========================================================
        # UPDATE DRIVER
        # ========================================================

        if self.driver:

            self.driver.status = Driver.Status.AVAILABLE

            self.driver.total_deliveries += 1

            self.driver.successful_deliveries += 1

            self.driver.save(
                update_fields=[
                    "status",
                    "total_deliveries",
                    "successful_deliveries",
                ]
            )
    def mark_cancelled(self):

            self.status = ShipmentStatus.CANCELLED

            self.save(
                update_fields=[
                    "status",
                ]
            )

            if self.driver:

                self.driver.status = Driver.Status.AVAILABLE
                self.driver.cancelled_deliveries += 1

                self.driver.save(
                    update_fields=[
                        "status",
                        "cancelled_deliveries",
                    ]
                )

    def mark_returned(self):

        self.status = ShipmentStatus.RETURNED

        self.save(
            update_fields=[
                "status",
            ]
        )

        if self.driver:

            self.driver.status = Driver.Status.AVAILABLE

            self.driver.save(
                update_fields=[
                    "status",
                ]
            )


class PaymentStatus(models.TextChoices):
    CREATED = "CREATED", "Created"
    PAID = "PAID", "Paid"
    FAILED = "FAILED", "Failed"


class Payment(models.Model):

    shipment = models.ForeignKey(
        Shipment,
        on_delete=models.CASCADE,
        related_name="payments",
    )

    razorpay_order_id = models.CharField(
        max_length=100,
        unique=True,
    )

    razorpay_payment_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    razorpay_signature = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    currency = models.CharField(
        max_length=10,
        default="INR",
    )

    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.CREATED,
        db_index=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    paid_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["shipment"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return (
            f"{self.shipment.tracking_number} - "
            f"{self.status} - ₹{self.amount}"
        )