from django.conf import settings
from django.db import models
from django.utils import timezone


class ContactStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    RESOLVED = "RESOLVED", "Resolved"
    CLOSED = "CLOSED", "Closed"


class ContactCategory(models.TextChoices):
    GENERAL = "GENERAL", "General Inquiry"
    SHIPMENT = "SHIPMENT", "Shipment Issue"
    DELIVERY = "DELIVERY", "Delivery Issue"
    PAYMENT = "PAYMENT", "Payment"
    COMPLAINT = "COMPLAINT", "Complaint"
    FEEDBACK = "FEEDBACK", "Feedback"
    OTHER = "OTHER", "Other"


class Contact(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="contact_requests",
        null=True,
        blank=True,
    )

    name = models.CharField(
        max_length=150,
    )

    email = models.EmailField()

    phone = models.CharField(
        max_length=20,
        blank=True,
    )

    subject = models.CharField(
        max_length=200,
    )

    message = models.TextField()

    category = models.CharField(
        max_length=20,
        choices=ContactCategory.choices,
        default=ContactCategory.GENERAL,
        db_index=True,
    )

    status = models.CharField(
        max_length=20,
        choices=ContactStatus.choices,
        default=ContactStatus.PENDING,
        db_index=True,
    )

    admin_reply = models.TextField(
        blank=True,
    )

    replied_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="replied_contacts",
        null=True,
        blank=True,
    )

    replied_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["category"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["user", "status"]),
        ]

        verbose_name = "Contact Request"
        verbose_name_plural = "Contact Requests"

    def __str__(self):
        return f"{self.subject} ({self.name})"

    @property
    def is_open(self):
        return self.status in (
            ContactStatus.PENDING,
            ContactStatus.IN_PROGRESS,
        )

    @property
    def is_closed(self):
        return self.status in (
            ContactStatus.RESOLVED,
            ContactStatus.CLOSED,
        )

    def mark_in_progress(self):
        if self.status == ContactStatus.PENDING:
            self.status = ContactStatus.IN_PROGRESS
            self.save(update_fields=["status"])

    def resolve(self, reply="", admin=None):
        self.admin_reply = reply

        if admin:
            self.replied_by = admin

        self.status = ContactStatus.RESOLVED
        self.replied_at = timezone.now()

        self.save(
            update_fields=[
                "admin_reply",
                "replied_by",
                "status",
                "replied_at",
            ]
        )

    def close(self):
        self.status = ContactStatus.CLOSED

        self.save(
            update_fields=[
                "status",
            ]
        )