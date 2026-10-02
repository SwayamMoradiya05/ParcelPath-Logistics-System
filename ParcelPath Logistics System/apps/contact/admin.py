from django.contrib import admin

from .models import Contact


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "email",
        "category",
        "status",
        "created_at",
        "replied_at",
    )

    search_fields = (
        "name",
        "email",
        "phone",
        "subject",
        "message",
    )

    list_filter = (
        "category",
        "status",
        "created_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "replied_at",
    )

    ordering = (
        "-created_at",
    )

    date_hierarchy = "created_at"

    list_per_page = 25

    list_select_related = (
        "user",
        "replied_by",
    )

    autocomplete_fields = (
        "user",
        "replied_by",
    )

    fieldsets = (
        (
            "Contact Information",
            {
                "fields": (
                    "user",
                    "name",
                    "email",
                    "phone",
                )
            },
        ),
        (
            "Request",
            {
                "fields": (
                    "subject",
                    "category",
                    "message",
                    "status",
                )
            },
        ),
        (
            "Admin Response",
            {
                "fields": (
                    "admin_reply",
                    "replied_by",
                    "replied_at",
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
        "mark_in_progress",
        "mark_resolved",
        "mark_closed",
    )

    @admin.action(description="Mark selected as In Progress")
    def mark_in_progress(self, request, queryset):
        for contact in queryset:
            contact.mark_in_progress()

        self.message_user(
            request,
            f"{queryset.count()} request(s) updated.",
        )

    @admin.action(description="Mark selected as Resolved")
    def mark_resolved(self, request, queryset):
        for contact in queryset:
            contact.status = "RESOLVED"
            contact.save(update_fields=["status"])

        self.message_user(
            request,
            f"{queryset.count()} request(s) resolved.",
        )

    @admin.action(description="Mark selected as Closed")
    def mark_closed(self, request, queryset):
        for contact in queryset:
            contact.close()

        self.message_user(
            request,
            f"{queryset.count()} request(s) closed.",
        )