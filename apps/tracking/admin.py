from django.contrib import admin

from .models import TrackingEvent


@admin.register(TrackingEvent)
class TrackingEventAdmin(admin.ModelAdmin):
    list_display = (
        "shipment",
        "status",
        "location",
        "updated_by",
        "has_coordinates",
        "created_at",
    )

    search_fields = (
        "shipment__tracking_number",
        "shipment__customer__company_name",
        "shipment__customer__user__first_name",
        "shipment__customer__user__last_name",
        "location",
        "description",
        "updated_by__first_name",
        "updated_by__last_name",
        "updated_by__email",
    )

    list_filter = (
        "status",
        "location",
        "created_at",
    )

    readonly_fields = (
        "coordinates_display",
        "google_maps_link",
        "created_at",
    )

    ordering = (
        "-created_at",
    )

    date_hierarchy = "created_at"

    list_per_page = 25

    list_select_related = (
        "shipment",
        "updated_by",
    )

    autocomplete_fields = (
        "shipment",
        "updated_by",
    )

    fieldsets = (
        (
            "Tracking Information",
            {
                "fields": (
                    "shipment",
                    "status",
                    "updated_by",
                )
            },
        ),
        (
            "Location Details",
            {
                "fields": (
                    "location",
                    "description",
                    "latitude",
                    "longitude",
                    "coordinates_display",
                    "google_maps_link",
                )
            },
        ),
        (
            "Timestamp",
            {
                "fields": (
                    "created_at",
                )
            },
        ),
    )

    @admin.display(
        boolean=True,
        description="GPS",
    )
    def has_coordinates(self, obj):
        return obj.has_coordinates

    @admin.display(
        description="Coordinates",
    )
    def coordinates_display(self, obj):
        if obj.has_coordinates:
            return f"{obj.latitude}, {obj.longitude}"
        return "-"

    @admin.display(
        description="Google Maps",
    )
    def google_maps_link(self, obj):
        if obj.google_maps_url:
            return obj.google_maps_url
        return "-"