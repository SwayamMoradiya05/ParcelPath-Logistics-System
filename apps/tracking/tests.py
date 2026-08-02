from decimal import Decimal

from django.test import TestCase

from apps.accounts.models import User
from apps.customers.models import Customer
from apps.shipments.models import Shipment
from apps.tracking.models import TrackingEvent
from apps.tracking.models import TrackingStatus


class TrackingModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="customer@test.com",
            password="Password@123",
        )

        self.customer = Customer.objects.create(
            user=self.user,
            address_line_1="Main Road",
            city="Surat",
            state="Gujarat",
            postal_code="395006",
        )

        self.shipment = Shipment.objects.create(
            customer=self.customer,
            created_by=self.user,
            sender_name="John",
            sender_phone="9999999999",
            sender_address="Surat",
            receiver_name="Rahul",
            receiver_phone="8888888888",
            receiver_address="Ahmedabad",
            package_type="Documents",
            weight=Decimal("1.5"),
            length=Decimal("10"),
            width=Decimal("10"),
            height=Decimal("10"),
        )

    def test_tracking_event_creation(self):
        event = TrackingEvent.objects.create(
            shipment=self.shipment,
            status=TrackingStatus.IN_TRANSIT,
            location="Vadodara Hub",
            description="Package reached sorting hub.",
        )

        self.assertEqual(
            event.shipment,
            self.shipment,
        )

        self.assertEqual(
            event.status,
            TrackingStatus.IN_TRANSIT,
        )

    def test_tracking_order(self):
        TrackingEvent.objects.create(
            shipment=self.shipment,
            status=TrackingStatus.PICKED_UP,
            location="Surat",
            description="Picked up",
        )

        TrackingEvent.objects.create(
            shipment=self.shipment,
            status=TrackingStatus.IN_TRANSIT,
            location="Bharuch",
            description="In Transit",
        )

        self.assertEqual(
            self.shipment.tracking_events.count(),
            3,  # includes initial event created by signal
        )