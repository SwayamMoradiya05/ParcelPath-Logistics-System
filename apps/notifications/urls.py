from django.urls import path

from . import views

app_name = "notifications"

urlpatterns = [
    # ======================================================
    # Notification List
    # ======================================================
    path(
        "",
        views.notification_list,
        name="list",
    ),

    # ======================================================
    # Notification Actions
    # ======================================================
    path(
        "<int:pk>/",
        views.notification_read,
        name="read",
    ),
    path(
        "<int:pk>/delete/",
        views.notification_delete,
        name="delete",
    ),

    # ======================================================
    # Bulk Actions
    # ======================================================
    path(
        "mark-all-read/",
        views.mark_all_read,
        name="mark_all_read",
    ),

    path(
    "delete-all/",
    views.delete_all_notifications,
    name="delete_all",
    ),
]