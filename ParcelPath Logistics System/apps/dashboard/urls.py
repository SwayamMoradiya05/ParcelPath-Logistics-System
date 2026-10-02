from django.urls import path

from . import admin_views, views


app_name = "dashboard"


urlpatterns = [

    # ==========================================================
    # NORMAL USER DASHBOARD
    # ==========================================================

    path(
        "",
        views.dashboard,
        name="dashboard",
    ),

    path(
        "legacy/",
        views.dashboard,
        name="legacy_dashboard",
    ),


    # ==========================================================
    # ADMIN DASHBOARD
    # ==========================================================

    path(
        "admin/",
        admin_views.dashboard,
        name="admin_dashboard",
    ),


    # ==========================================================
    # GENERIC ADMIN MODEL CRUD
    #
    # IMPORTANT:
    # These routes are placed BEFORE the generic
    # contact/route action routes.
    #
    # This ensures:
    # /contacts/3/edit/   -> model_update
    # /contacts/3/delete/ -> model_delete
    #
    # instead of:
    # /contacts/3/edit/ -> contact_action(action="edit")
    # ==========================================================

    path(
        "<str:model_key>/create/",
        admin_views.model_create,
        name="model_create",
    ),

    path(
        "<str:model_key>/<int:pk>/edit/",
        admin_views.model_update,
        name="model_update",
    ),

    path(
        "<str:model_key>/<int:pk>/delete/",
        admin_views.model_delete,
        name="model_delete",
    ),

    path(
        "<str:model_key>/<int:pk>/",
        admin_views.model_detail,
        name="model_detail",
    ),

    path(
        "<str:model_key>/",
        admin_views.model_list,
        name="model_list",
    ),


    # ==========================================================
    # SHIPMENT ADMIN ACTIONS
    # ==========================================================

    path(
        "shipments/<int:pk>/status/<str:status>/",
        admin_views.shipment_status,
        name="shipment_status",
    ),

    path(
        "shipments/<int:pk>/assign-driver/",
        admin_views.shipment_assign_driver,
        name="shipment_assign_driver",
    ),


    # ==========================================================
    # DRIVER ADMIN ACTIONS
    # ==========================================================

    path(
        "drivers/<int:pk>/verify/",
        admin_views.driver_verify,
        name="driver_verify",
    ),


    # ==========================================================
    # CONTACT ADMIN ACTIONS
    #
    # These now come AFTER generic CRUD.
    #
    # Therefore:
    # edit   -> model_update
    # delete -> model_delete
    # progress/resolve/close -> contact_action
    # ==========================================================

    path(
        "contacts/<int:pk>/<str:action>/",
        admin_views.contact_action,
        name="contact_action",
    ),


    # ==========================================================
    # NOTIFICATION ADMIN ACTIONS
    # ==========================================================

    path(
        "notifications/<int:pk>/toggle-read/",
        admin_views.notification_read,
        name="notification_read",
    ),


    # ==========================================================
    # ROUTE ADMIN ACTIONS
    # ==========================================================

    path(
        "routes/<int:pk>/<str:action>/",
        admin_views.route_action,
        name="route_action",
    ),
]