from django.urls import path

from . import views

app_name = "customers"

urlpatterns = [
    path(
        "",
        views.customer_list,
        name="customer_list",
    ),
    path(
        "create/",
        views.customer_create,
        name="customer_create",
    ),
    path(
        "<int:pk>/",
        views.customer_detail,
        name="customer_detail",
    ),
    path(
        "<int:pk>/edit/",
        views.customer_update,
        name="customer_update",
    ),
    path(
        "<int:pk>/delete/",
        views.customer_delete,
        name="customer_delete",
    ),
    path(
        "dashboard/",
        views.dashboard,
        name="dashboard",
    ),
]