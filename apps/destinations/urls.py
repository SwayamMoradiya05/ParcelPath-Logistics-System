from django.urls import path

from . import views

app_name = "destinations"

urlpatterns = [
    path(
        "",
        views.destination_list,
        name="list",
    ),
    path(
        "create/",
        views.destination_create,
        name="create",
    ),
    path(
        "<int:pk>/",
        views.destination_detail,
        name="detail",
    ),
    path(
        "<int:pk>/edit/",
        views.destination_update,
        name="update",
    ),
    path(
        "<int:pk>/delete/",
        views.destination_delete,
        name="delete",
    ),
]