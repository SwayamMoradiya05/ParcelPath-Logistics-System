from django.urls import path

from . import views

app_name = "drivers"

urlpatterns = [
    path(
        "",
        views.driver_list,
        name="driver_list",
    ),

    path(
        "dashboard/",
        views.dashboard,
        name="dashboard",
    ),

    path(
        "complete-profile/",
        views.complete_profile,
        name="complete_profile",
    ),

    path(
        "create/",
        views.driver_create,
        name="driver_create",
    ),

    path(
        "<int:pk>/",
        views.driver_detail,
        name="driver_detail",
    ),

    path(
        "<int:pk>/edit/",
        views.driver_update,
        name="driver_update",
    ),

    path(
        "<int:pk>/delete/",
        views.driver_delete,
        name="driver_delete",
    ),
    
    path(
        "deliveries/",
        views.deliveries,
        name="deliveries",
    ),

    path(
        "delivery/<int:pk>/",
        views.delivery_details,
        name="delivery_details",
    ),

    path(
        "route/",
        views.route,
        name="route",
    ),

    path(
        "history/",
        views.history,
        name="history",
    ),
    path(
        "toggle-availability/",
        views.toggle_availability,
        name="toggle_availability",
    ),
]