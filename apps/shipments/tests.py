from decimal import Decimal

from django.test import TestCase

from apps.accounts.models import User
from apps.customers.models import Customer
from apps.shipments.models import Shipment, ShipmentStatus


class ShipmentModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="customer@test.com",
            password="Password@123",
            first_name="John",
            last_name="Doe",
        )

        self.customer = Customer.objects.create(
            user=self.user,
            address_line_1="Ring Road",
            city="Surat",
            state="Gujarat",
            postal_code="395006",
        )

    def test_create_shipment(self):
        shipment = Shipment.objects.create(
            customer=self.customer,
            created_by=self.user,
            sender_name="John",
            sender_phone="9876543210",
            sender_address="Surat",
            receiver_name="Rahul",
            receiver_phone="9876500000",
            receiver_address="Ahmedabad",
            package_type="Documents",
            weight=Decimal("2.50"),
            length=Decimal("10"),
            width=Decimal("8"),
            height=Decimal("5"),
            shipping_cost=Decimal("250"),
        )

        self.assertIsNotNone(
            shipment.tracking_number
        )

        self.assertEqual(
            shipment.status,
            ShipmentStatus.PENDING,
        )

    def test_volume(self):
        shipment = Shipment.objects.create(
            customer=self.customer,
            created_by=self.user,
            sender_name="A",
            sender_phone="1111111111",
            sender_address="A",
            receiver_name="B",
            receiver_phone="2222222222",
            receiver_address="B",
            package_type="Box",
            weight=Decimal("1"),
            length=Decimal("10"),
            width=Decimal("10"),
            height=Decimal("10"),
        )

        self.assertEqual(
            shipment.volume,
            Decimal("1000"),
        )