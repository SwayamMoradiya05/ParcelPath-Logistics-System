from django.db import transaction
from django.utils import timezone

from .models import Contact, ContactStatus


class ContactService:

    @staticmethod
    @transaction.atomic
    def create(user, **data):
        contact = Contact(**data)

        if user and user.is_authenticated:
            contact.user = user

        contact.save()

        return contact

    @staticmethod
    def get_all():
        return Contact.objects.select_related(
            "user",
            "replied_by",
        ).order_by(
            "-created_at",
        )

    @staticmethod
    def get_by_id(contact_id):
        return Contact.objects.select_related(
            "user",
            "replied_by",
        ).get(
            pk=contact_id,
        )

    @staticmethod
    def pending():
        return Contact.objects.filter(
            status=ContactStatus.PENDING,
        ).order_by(
            "-created_at",
        )

    @staticmethod
    def in_progress():
        return Contact.objects.filter(
            status=ContactStatus.IN_PROGRESS,
        ).order_by(
            "-created_at",
        )

    @staticmethod
    def resolved():
        return Contact.objects.filter(
            status=ContactStatus.RESOLVED,
        ).order_by(
            "-created_at",
        )

    @staticmethod
    @transaction.atomic
    def mark_in_progress(contact):
        contact.mark_in_progress()
        return contact

    @staticmethod
    @transaction.atomic
    def resolve(contact, reply, admin):
        contact.resolve(
            reply=reply,
            admin=admin,
        )
        return contact

    @staticmethod
    @transaction.atomic
    def close(contact):
        contact.close()
        return contact

    @staticmethod
    @transaction.atomic
    def update(contact, **data):
        for field, value in data.items():
            setattr(contact, field, value)

        contact.save()

        return contact

    @staticmethod
    @transaction.atomic
    def delete(contact):
        contact.delete()

    @staticmethod
    def dashboard_statistics():
        return {
            "total": Contact.objects.count(),
            "pending": Contact.objects.filter(
                status=ContactStatus.PENDING,
            ).count(),
            "in_progress": Contact.objects.filter(
                status=ContactStatus.IN_PROGRESS,
            ).count(),
            "resolved": Contact.objects.filter(
                status=ContactStatus.RESOLVED,
            ).count(),
            "closed": Contact.objects.filter(
                status=ContactStatus.CLOSED,
            ).count(),
        }

    @staticmethod
    def recent(limit=10):
        return Contact.objects.select_related(
            "user",
        ).order_by(
            "-created_at",
        )[:limit]

    @staticmethod
    def user_contacts(user):
        return Contact.objects.filter(
            user=user,
        ).order_by(
            "-created_at",
        )

    @staticmethod
    def unresolved():
        return Contact.objects.filter(
            status__in=[
                ContactStatus.PENDING,
                ContactStatus.IN_PROGRESS,
            ]
        ).order_by(
            "-created_at",
        )