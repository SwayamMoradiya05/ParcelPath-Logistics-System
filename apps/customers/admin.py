from django.contrib import admin

from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "customer_id",
        "display_name",
        "user",
        "city",
        "state",
        "is_verified",
        "total_shipments",
        "completed_shipments",
        "cancelled_shipments",
        "completion_percentage",
        "created_at",
    )

    search_fields = (
        "customer_id",
        "user__email",
        "user__first_name",
        "user__last_name",
        "company_name",
        "gst_number",
        "city",
        "state",
        "postal_code",
    )

    list_filter = (
        "is_verified",
        "city",
        "state",
        "country",
        "created_at",
    )

    readonly_fields = (
        "customer_id",
        "total_shipments",
        "completed_shipments",
        "cancelled_shipments",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )

    date_hierarchy = "created_at"

    list_per_page = 25

    list_select_related = (
        "user",
    )

    autocomplete_fields = (
        "user",
    )

    fieldsets = (
        (
            "Customer Information",
            {
                "fields": (
                    "customer_id",
                    "user",
                    "company_name",
                    "gst_number",
                    "is_verified",
                    "profile_image",
                )
            },
        ),
        (
            "Contact Information",
            {
                "fields": (
                    "alternate_phone",
                )
            },
        ),
        (
            "Address",
            {
                "fields": (
                    "address_line_1",
                    "address_line_2",
                    "city",
                    "state",
                    "country",
                    "postal_code",
                )
            },
        ),
        (
            "Shipment Statistics",
            {
                "fields": (
                    "total_shipments",
                    "completed_shipments",
                    "cancelled_shipments",
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

    @admin.display(
        description="Customer"
    )
    def display_name(self, obj):
        return obj.display_name

    @admin.display(
        description="Completion %",
    )
    def completion_percentage(self, obj):
        return f"{obj.completion_rate}%"