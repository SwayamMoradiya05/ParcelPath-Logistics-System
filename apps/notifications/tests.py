from django.test import TestCase

from apps.accounts.models import User

from .models import Notification
from .models import NotificationType


class NotificationModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="demo@test.com",
            password="Password@123",
        )

    def test_notification_creation(self):
        notification = Notification.objects.create(
            user=self.user,
            title="Test Notification",
            message="Notification Body",
            notification_type=NotificationType.INFO,
        )

        self.assertEqual(
            notification.user,
            self.user,
        )

        self.assertFalse(
            notification.is_read,
        )

    def test_notification_string(self):
        notification = Notification.objects.create(
            user=self.user,
            title="Shipment",
            message="Created",
        )

        self.assertIn(
            "Shipment",
            str(notification),
        )