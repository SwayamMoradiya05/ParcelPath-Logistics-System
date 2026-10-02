from django.apps import AppConfig


class ShipmentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.shipments"

    def ready(self):
     from . import signals