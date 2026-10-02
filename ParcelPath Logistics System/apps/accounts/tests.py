from django.test import TestCase

from .models import User, UserRole


class UserModelTest(TestCase):

    def test_create_customer(self):
        user = User.objects.create_user(
            email="customer@example.com",
            password="Test@12345",
            first_name="John",
            last_name="Doe",
            role=UserRole.CUSTOMER,
        )

        self.assertEqual(
            user.email,
            "customer@example.com",
        )

        self.assertTrue(user.check_password("Test@12345"))
        self.assertTrue(user.is_customer)

    def test_create_driver(self):
        user = User.objects.create_user(
            email="driver@example.com",
            password="Driver@123",
            role=UserRole.DRIVER,
        )

        self.assertTrue(user.is_driver)

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            email="admin@example.com",
            password="Admin@123",
        )

        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)
        self.assertEqual(admin.role, UserRole.ADMIN)

    def test_full_name(self):
        user = User.objects.create_user(
            email="demo@example.com",
            password="Password@123",
            first_name="Parcel",
            last_name="Path",
        )

        self.assertEqual(
            user.full_name,
            "Parcel Path",
        )