from django.test import TestCase

from apps.accounts.models import User
from apps.drivers.models import Driver
from apps.routes.models import Route, RouteStatus


class RouteModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="driver@test.com",
            password="Password@123",
        )

        self.driver = Driver.objects.create(
            user=self.user,
            license_number="DL123456",
            license_expiry="2030-12-31",
            vehicle_type=Driver.VehicleType.BIKE,
            vehicle_number="GJ05AB1234",
            vehicle_model="Honda Shine",
            vehicle_capacity=50,
        )

    def test_create_route(self):
        route = Route.objects.create(
            name="Surat City Route",
            driver=self.driver,
            origin="Surat Hub",
            destination="Adajan",
            total_distance=18.5,
            estimated_duration=45,
        )

        self.assertTrue(
            route.route_code.startswith("RTE")
        )

    def test_default_status(self):
        route = Route.objects.create(
            name="Test Route",
            origin="A",
            destination="B",
        )

        self.assertEqual(
            route.status,
            RouteStatus.PLANNED
        )