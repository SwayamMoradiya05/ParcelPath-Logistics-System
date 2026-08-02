from django.db import models


class Destination(models.Model):
    destination_code = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
    )

    name = models.CharField(
        max_length=150,
        db_index=True,
    )

    city = models.CharField(
        max_length=100,
        db_index=True,
    )

    state = models.CharField(
        max_length=100,
    )

    country = models.CharField(
        max_length=100,
        default="India",
    )

    postal_code = models.CharField(
        max_length=10,
    )

    address = models.TextField()

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "city",
            "name",
        ]

        indexes = [
            models.Index(
                fields=[
                    "city",
                ]
            ),
            models.Index(
                fields=[
                    "state",
                ]
            ),
            models.Index(
                fields=[
                    "country",
                ]
            ),
            models.Index(
                fields=[
                    "is_active",
                ]
            ),
        ]

        verbose_name = "Destination"
        verbose_name_plural = "Destinations"

    def __str__(self):
        return f"{self.name} ({self.city})"

    def save(self, *args, **kwargs):
        if not self.destination_code:
            prefix = self.city[:3].upper() if self.city else "DST"
            last = (
                Destination.objects.filter(
                    destination_code__startswith=prefix,
                )
                .count()
                + 1
            )

            self.destination_code = f"{prefix}{last:04d}"

        self.name = self.name.strip()
        self.city = self.city.strip().title()
        self.state = self.state.strip().title()
        self.country = self.country.strip().title()
        self.postal_code = self.postal_code.strip().upper()
        self.address = self.address.strip()

        super().save(*args, **kwargs)

    @property
    def full_address(self):
        return (
            f"{self.address}, "
            f"{self.city}, "
            f"{self.state}, "
            f"{self.country} - "
            f"{self.postal_code}"
        )

    @property
    def coordinates(self):
        if self.latitude is not None and self.longitude is not None:
            return f"{self.latitude}, {self.longitude}"
        return "-"

    @property
    def google_maps_url(self):
        if self.latitude is not None and self.longitude is not None:
            return (
                "https://www.google.com/maps/search/?api=1"
                f"&query={self.latitude},{self.longitude}"
            )
        return ""

    def activate(self):
        if not self.is_active:
            self.is_active = True
            self.save(
                update_fields=[
                    "is_active",
                ]
            )

    def deactivate(self):
        if self.is_active:
            self.is_active = False
            self.save(
                update_fields=[
                    "is_active",
                ]
            )