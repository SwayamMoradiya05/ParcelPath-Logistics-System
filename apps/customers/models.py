from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.utils.text import slugify


class Customer(models.Model):
    customer_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        db_index=True,
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer_profile",
    )

    company_name = models.CharField(
        max_length=200,
        blank=True,
    )

    gst_number = models.CharField(
        max_length=20,
        blank=True,
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
        upload_to="customers/",
        blank=True,
        null=True,
    )

    address_line_1 = models.CharField(
        max_length=255,
    )

    address_line_2 = models.CharField(
        max_length=255,
        blank=True,
    )

    city = models.CharField(
        max_length=100,
        db_index=True,
    )

    state = models.CharField(
        max_length=100,
        db_index=True,
    )

    country = models.CharField(
        max_length=100,
        default="India",
    )

    postal_code = models.CharField(
        max_length=20,
    )

    total_shipments = models.PositiveIntegerField(
        default=0,
    )

    completed_shipments = models.PositiveIntegerField(
        default=0,
    )

    cancelled_shipments = models.PositiveIntegerField(
        default=0,
    )

    is_verified = models.BooleanField(
        default=False,
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
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

        ordering = [
            "user__first_name",
            "user__last_name",
        ]

        indexes = [
            models.Index(fields=["customer_id"]),
            models.Index(fields=["city"]),
            models.Index(fields=["state"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["is_verified"]),
        ]

    def __str__(self):
        return self.user.full_name or self.user.email

    def save(self, *args, **kwargs):
        if self.gst_number:
            self.gst_number = self.gst_number.upper().strip()

        if self.alternate_phone:
            self.alternate_phone = self.alternate_phone.strip()

        if not self.customer_id:
            last_customer = (
                Customer.objects.order_by("-id")
                .only("id")
                .first()
            )

            next_id = (
                last_customer.id + 1
                if last_customer
                else 1
            )

            self.customer_id = f"CUST{next_id:06d}"

        super().save(*args, **kwargs)

    @property
    def full_address(self):
        address = [
            self.address_line_1,
            self.address_line_2,
            self.city,
            self.state,
            self.country,
            self.postal_code,
        ]

        return ", ".join(
            filter(None, address)
        )

    @property
    def pending_shipments(self):
        return (
            self.total_shipments
            - self.completed_shipments
            - self.cancelled_shipments
        )

    @property
    def completion_rate(self):
        if self.total_shipments == 0:
            return 0

        return round(
            (
                self.completed_shipments
                / self.total_shipments
            )
            * 100,
            2,
        )

    @property
    def display_name(self):
        if self.company_name:
            return self.company_name

        return self.user.full_name or self.user.email

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

    def increment_total_shipments(self):
        self.total_shipments += 1
        self.save(
            update_fields=[
                "total_shipments",
            ]
        )

    def increment_completed_shipments(self):
        self.completed_shipments += 1
        self.save(
            update_fields=[
                "completed_shipments",
            ]
        )

    def increment_cancelled_shipments(self):
        self.cancelled_shipments += 1
        self.save(
            update_fields=[
                "cancelled_shipments",
            ]
        )