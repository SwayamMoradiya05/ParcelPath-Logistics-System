from django.urls import path

from . import views

app_name = "contact"

urlpatterns = [
    path(
        "",
        views.contact_list,
        name="list",
    ),
    path(
        "create/",
        views.contact_create,
        name="create",
    ),
    path(
        "<int:pk>/",
        views.contact_detail,
        name="detail",
    ),
    path(
        "<int:pk>/reply/",
        views.contact_reply,
        name="reply",
    ),
    path(
        "<int:pk>/delete/",
        views.contact_delete,
        name="delete",
    ),
]