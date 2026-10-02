from django.db import transaction
from django.db.models import Count

from .models import Destination


class DestinationService:

    @staticmethod
    def get_all():
        return Destination.objects.order_by(
            "city",
            "name",
        )

    @staticmethod
    def get_by_id(destination_id):
        return Destination.objects.get(
            pk=destination_id,
        )

    @staticmethod
    @transaction.atomic
    def create(**data):
        return Destination.objects.create(
            **data,
        )

    @staticmethod
    @transaction.atomic
    def update(destination, **data):
        for field, value in data.items():
            setattr(destination, field, value)

        destination.save()

        return destination

    @staticmethod
    @transaction.atomic
    def delete(destination):
        destination.delete()

    @staticmethod
    def active():
        return Destination.objects.filter(
            is_active=True,
        ).order_by(
            "city",
            "name",
        )

    @staticmethod
    def inactive():
        return Destination.objects.filter(
            is_active=False,
        ).order_by(
            "city",
            "name",
        )

    @staticmethod
    @transaction.atomic
    def activate(destination):
        destination.activate()
        return destination

    @staticmethod
    @transaction.atomic
    def deactivate(destination):
        destination.deactivate()
        return destination

    @staticmethod
    def search(query):
        return Destination.objects.filter(
            name__icontains=query,
        ).order_by(
            "city",
            "name",
        )

    @staticmethod
    def dashboard_statistics():
        return {
            "total": Destination.objects.count(),
            "active": Destination.objects.filter(
                is_active=True,
            ).count(),
            "inactive": Destination.objects.filter(
                is_active=False,
            ).count(),
        }   