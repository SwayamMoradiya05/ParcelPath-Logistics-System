from django.contrib import admin

from .models import Route, RouteShipment


class RouteShipmentInline(admin.TabularInline):
    model = RouteShipment
    extra = 0

    autocomplete_fields = (
        "shipment",
    )

    fields = (
        "shipment",
        "stop_number",
        "delivered",
    )

    ordering = (
        "stop_number",
    )


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = (
        "route_code",
        "name",
        "driver",
        "origin",
        "destination",
        "status",
        "total_shipments_display",
        "completion_display",
        "created_at",
    )

    search_fields = (
        "route_code",
        "name",
        "origin",
        "destination",
        "driver__user__first_name",
        "driver__user__last_name",
        "driver__user__email",
    )

    list_filter = (
        "status",
        "created_at",
    )

    readonly_fields = (
        "route_code",
        "total_shipments_display",
        "delivered_shipments_display",
        "pending_shipments_display",
        "completion_display",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )

    date_hierarchy = "created_at"

    list_per_page = 25

    list_select_related = (
        "driver",
        "driver__user",
    )

    autocomplete_fields = (
        "driver",
    )

    fieldsets = (
        (
            "Route Information",
            {
                "fields": (
                    "route_code",
                    "name",
                    "driver",
                    "status",
                )
            },
        ),
        (
            "Route Details",
            {
                "fields": (
                    "origin",
                    "destination",
                    "total_distance",
                    "estimated_duration",
                )
            },
        ),
        (
            "Statistics",
            {
                "fields": (
                    "total_shipments_display",
                    "delivered_shipments_display",
                    "pending_shipments_display",
                    "completion_display",
                )
            },
        ),
        (
            "Additional Information",
            {
                "fields": (
                    "notes",
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

    inlines = [
        RouteShipmentInline,
    ]

    @admin.display(
        description="Shipments",
    )
    def total_shipments_display(self, obj):
        return obj.total_shipments

    @admin.display(
        description="Delivered",
    )
    def delivered_shipments_display(self, obj):
        return obj.delivered_shipments

    @admin.display(
        description="Pending",
    )
    def pending_shipments_display(self, obj):
        return obj.pending_shipments

    @admin.display(
        description="Completion %",
    )
    def completion_display(self, obj):
        return f"{obj.completion_percentage}%"


@admin.register(RouteShipment)
class RouteShipmentAdmin(admin.ModelAdmin):
    list_display = (
        "route",
        "shipment",
        "stop_number",
        "delivered",
    )

    search_fields = (
        "route__route_code",
        "shipment__tracking_number",
    )

    list_filter = (
        "delivered",
        "route__status",
    )

    ordering = (
        "route",
        "stop_number",
    )

    list_per_page = 25

    list_select_related = (
        "route",
        "shipment",
    )

    autocomplete_fields = (
        "route",
        "shipment",
    )