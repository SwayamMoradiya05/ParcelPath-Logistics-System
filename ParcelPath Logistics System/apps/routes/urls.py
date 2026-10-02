from django.urls import path

from . import views

app_name = "routes"

urlpatterns = [
    # ======================================================
    # Route CRUD
    # ======================================================
    path(
        "",
        views.route_list,
        name="route_list",
    ),
    path(
        "create/",
        views.route_create,
        name="route_create",
    ),
    path(
        "<int:pk>/",
        views.route_detail,
        name="route_detail",
    ),
    path(
        "<int:pk>/edit/",
        views.route_update,
        name="route_update",
    ),
    path(
        "<int:pk>/delete/",
        views.route_delete,
        name="route_delete",
    ),

    # ======================================================
    # Driver Assignment
    # ======================================================
    path(
        "<int:pk>/assign-driver/",
        views.assign_driver,
        name="assign_driver",
    ),

    # ======================================================
    # Route Workflow
    # ======================================================
    path(
        "<int:pk>/status/<str:status>/",
        views.update_status,
        name="update_status",
    ),
]