from django.urls import path

from . import views

app_name = "shipments"

urlpatterns = [
    path(
        "",
        views.shipment_list,
        name="shipment_list",
    ),
    path(
        "create/",
        views.shipment_create,
        name="shipment_create",
    ),
    path(
        "<int:pk>/",
        views.shipment_detail,
        name="shipment_detail",
    ),
    path(
        "<int:pk>/edit/",
        views.shipment_update,
        name="shipment_update",
    ),
    path(
        "<int:pk>/delete/",
        views.shipment_delete,
        name="shipment_delete",
    ),
    path(
        "<int:pk>/assign-driver/",
        views.assign_driver,
        name="assign_driver",
    ),

    # Driver updates shipment status
    path(
        "<int:pk>/driver-update/",
        views.driver_update_status,
        name="driver_update_status",
    ),

    # Admin status update
    path(
        "<int:pk>/status/<str:status>/",
        views.update_status,
        name="update_status",
    ),

    path(
        "available-drivers/",
        views.available_drivers,
        name="available_drivers",
    ),
    path(
        "<int:pk>/label/",
        views.shipment_label,
        name="shipment_label",
    ),
    path(
        "track/<str:tracking_number>/",
        views.track_shipment,
        name="track_shipment",
    ),
    path(
    "<int:pk>/label/pdf/",
    views.shipment_label_pdf,
    name="shipment_label_pdf",
    ),
    path(
    "<int:pk>/pay/",
    views.shipment_payment,
    name="shipment_payment",
    ),

    path(
        "<int:pk>/verify-payment/",
        views.verify_shipment_payment,
        name="verify_shipment_payment",
        ),

    path(
    "<int:pk>/receipt/",
    views.payment_receipt,
    name="payment_receipt",
),

    path(
        "<int:pk>/receipt/pdf/",
        views.payment_receipt_pdf,
        name="payment_receipt_pdf",
    ),
]