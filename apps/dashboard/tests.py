from django.test import Client
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User


class DashboardViewTest(TestCase):

    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            email="admin@test.com",
            password="Password@123",
            role="ADMIN",
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(
            reverse("dashboard:dashboard")
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_dashboard_authenticated(self):
        self.client.login(
            email="admin@test.com",
            password="Password@123",
        )

        response = self.client.get(
            reverse("dashboard:dashboard")
        )

        self.assertEqual(
            response.status_code,
            200,
        )