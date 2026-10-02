from datetime import date, timedelta

from django.test import TestCase

from apps.accounts.models import User
from .models import Driver


class DriverModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="driver@test.com",
            password="Password@123",
            first_name="Rahul",
            last_name="Sharma",
        )

    def test_driver_creation(self):
        driver = Driver.objects.create(
            user=self.user,
            license_number="LIC123456",
            license_expiry=date.today() + timedelta(days=365),
            vehicle_type=Driver.VehicleType.BIKE,
            vehicle_number="GJ05AB1234",
            vehicle_model="Honda Shine",
            vehicle_capacity=50,
        )

        self.assertTrue(
            driver.driver_id.startswith("DRV")
        )

        self.assertEqual(
            driver.status,
            Driver.Status.AVAILABLE,
        )

    def test_driver_availability(self):
        driver = Driver.objects.create(
            user=self.user,
            license_number="LIC654321",
            license_expiry=date.today() + timedelta(days=365),
            vehicle_type=Driver.VehicleType.VAN,
            vehicle_number="GJ01XY5678",
            vehicle_model="Tata Ace",
            vehicle_capacity=500,
        )

        self.assertTrue(driver.availability)