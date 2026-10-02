from django.contrib import admin

from .models import Destination


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = (
        "destination_code",
        "name",
        "city",
        "state",
        "country",
        "postal_code",
        "is_active",
    )

    search_fields = (
        "destination_code",
        "name",
        "city",
        "state",
        "country",
        "postal_code",
        "address",
    )

    list_filter = (
        "country",
        "state",
        "is_active",
        "created_at",
    )

    readonly_fields = (
        "destination_code",
        "created_at",
        "updated_at",
    )

    ordering = (
        "city",
        "name",
    )

    date_hierarchy = "created_at"

    list_per_page = 25

    fieldsets = (
        (
            "Destination",
            {
                "fields": (
                    "destination_code",
                    "name",
                    "is_active",
                )
            },
        ),
        (
            "Location",
            {
                "fields": (
                    "address",
                    "city",
                    "state",
                    "country",
                    "postal_code",
                )
            },
        ),
        (
            "Coordinates",
            {
                "fields": (
                    "latitude",
                    "longitude",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    actions = (
        "activate_destinations",
        "deactivate_destinations",
    )

    @admin.action(description="Activate selected destinations")
    def activate_destinations(self, request, queryset):
        updated = queryset.update(is_active=True)

        self.message_user(
            request,
            f"{updated} destination(s) activated.",
        )

    @admin.action(description="Deactivate selected destinations")
    def deactivate_destinations(self, request, queryset):
        updated = queryset.update(is_active=False)

        self.message_user(
            request,
            f"{updated} destination(s) deactivated.",
        )