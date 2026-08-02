from django.urls import path
from . import views

app_name = "tracking"

urlpatterns = [
    path(
        "",
        views.public_tracking,
        name="track",
    ),

    path(
        "list/",
        views.tracking_list,
        name="tracking_list",
    ),

    path(
        "shipment/<int:shipment_id>/add/",
        views.add_tracking_event,
        name="add_tracking_event",
    ),

    path(
        "<str:tracking_number>/",
        views.shipment_tracking,
        name="shipment_tracking",
    ),
]