from django.contrib import admin

from .models import Driver


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = (
        "driver_id",
        "display_name",
        "user",
        "vehicle_number",
        "vehicle_type",
        "status",
        "rating",
        "is_verified",
        "total_deliveries",
        "successful_deliveries",
        "cancelled_deliveries",
        "completion_percentage",
        "joined_date",
    )

    search_fields = (
        "driver_id",
        "user__email",
        "user__first_name",
        "user__last_name",
        "license_number",
        "vehicle_number",
        "vehicle_model",
        "alternate_phone",
    )

    list_filter = (
        "status",
        "vehicle_type",
        "is_verified",
        "joined_date",
        "created_at",
    )

    readonly_fields = (
        "driver_id",
        "rating",
        "total_deliveries",
        "successful_deliveries",
        "cancelled_deliveries",
        "joined_date",
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
            "Driver Information",
            {
                "fields": (
                    "driver_id",
                    "user",
                    "profile_image",
                    "alternate_phone",
                    "is_verified",
                )
            },
        ),
        (
            "License Information",
            {
                "fields": (
                    "license_number",
                    "license_expiry",
                )
            },
        ),
        (
            "Vehicle Information",
            {
                "fields": (
                    "vehicle_type",
                    "vehicle_number",
                    "vehicle_model",
                    "vehicle_capacity",
                )
            },
        ),
        (
            "Current Status",
            {
                "fields": (
                    "status",
                    "current_latitude",
                    "current_longitude",
                )
            },
        ),
        (
            "Delivery Statistics",
            {
                "fields": (
                    "rating",
                    "total_deliveries",
                    "successful_deliveries",
                    "cancelled_deliveries",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "joined_date",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    @admin.display(description="Driver")
    def display_name(self, obj):
        return obj.user.full_name or obj.user.email

    @admin.display(description="Completion %")
    def completion_percentage(self, obj):
        return f"{obj.completion_rate}%"

    def get_search_results(self, request, queryset, search_term):
        """
        Restrict Shipment admin autocomplete to verified,
        AVAILABLE drivers only.
        """

        queryset, use_distinct = super().get_search_results(
            request,
            queryset,
            search_term,
        )

        if (
            request.path.startswith("/admin/autocomplete/")
            and request.GET.get("app_label") == "shipments"
            and request.GET.get("model_name") == "shipment"
            and request.GET.get("field_name") == "driver"
        ):
            queryset = queryset.filter(
                is_verified=True,
                status=Driver.Status.AVAILABLE,
            )

        return queryset, use_distinct