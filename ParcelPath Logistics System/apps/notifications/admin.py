from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "title",
        "notification_type",
        "is_read",
        "created_at",
        "read_at",
    )

    search_fields = (
        "title",
        "message",
        "user__email",
        "user__first_name",
        "user__last_name",
    )

    list_filter = (
        "notification_type",
        "is_read",
        "created_at",
    )

    readonly_fields = (
        "created_at",
        "read_at",
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
            "Notification Information",
            {
                "fields": (
                    "user",
                    "title",
                    "message",
                    "notification_type",
                )
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "is_read",
                    "action_url",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "read_at",
                )
            },
        ),
    )

    actions = (
        "mark_selected_as_read",
        "mark_selected_as_unread",
    )

    @admin.action(description="Mark selected notifications as Read")
    def mark_selected_as_read(self, request, queryset):
        for notification in queryset:
            notification.mark_as_read()

        self.message_user(
            request,
            f"{queryset.count()} notification(s) marked as read.",
        )

    @admin.action(description="Mark selected notifications as Unread")
    def mark_selected_as_unread(self, request, queryset):
        for notification in queryset:
            notification.mark_as_unread()

        self.message_user(
            request,
            f"{queryset.count()} notification(s) marked as unread.",
        )