from django.contrib import admin

from .models import Shipment


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = (
        "tracking_number",
        "customer",
        "driver",
        "status",
        "package_type",
        "weight",
        "shipping_cost",
        "expected_delivery",
        "created_at",
    )

    search_fields = (
        "tracking_number",
        "sender_name",
        "sender_phone",
        "receiver_name",
        "receiver_phone",
        "customer__customer_id",
        "customer__company_name",
        "customer__user__first_name",
        "customer__user__last_name",
        "customer__user__email",
        "driver__user__first_name",
        "driver__user__last_name",
    )

    list_filter = (
        "status",
        "package_type",
        "created_at",
        "expected_delivery",
        "delivered_at",
    )

    readonly_fields = (
        "tracking_number",
        "volume_display",
        "chargeable_weight_display",
        "created_at",
        "updated_at",
        "delivered_at",
    )

    ordering = (
        "-created_at",
    )

    date_hierarchy = "created_at"

    list_per_page = 25

    list_select_related = (
        "customer",
        "driver",
        "created_by",
    )

    autocomplete_fields = (
        "customer",
        "driver",
        "created_by",
    )

    fieldsets = (
        (
            "Shipment Information",
            {
                "fields": (
                    "tracking_number",
                    "customer",
                    "driver",
                    "created_by",
                    "status",
                )
            },
        ),
        (
            "Sender Details",
            {
                "fields": (
                    "sender_name",
                    "sender_phone",
                    "sender_address",
                )
            },
        ),
        (
            "Receiver Details",
            {
                "fields": (
                    "receiver_name",
                    "receiver_phone",
                    "receiver_address",
                )
            },
        ),
        (
            "Package Details",
            {
                "fields": (
                    "package_type",
                    "weight",
                    "length",
                    "width",
                    "height",
                    "volume_display",
                    "chargeable_weight_display",
                )
            },
        ),
        (
            "Shipping",
            {
                "fields": (
                    "declared_value",
                    "shipping_cost",
                    "expected_delivery",
                    "delivered_at",
                    "remarks",
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

    @admin.display(
        description="Volume (cm³)",
    )
    def volume_display(self, obj):
        return obj.volume

    @admin.display(
        description="Chargeable Weight (kg)",
    )
    def chargeable_weight_display(self, obj):
        return obj.chargeable_weight