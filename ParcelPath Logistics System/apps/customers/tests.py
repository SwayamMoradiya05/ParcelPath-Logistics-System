from django.test import TestCase

from apps.accounts.models import User
from .models import Customer


class CustomerModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="customer@test.com",
            password="Password@123",
            first_name="John",
            last_name="Doe",
        )

    def test_create_customer(self):
        customer = Customer.objects.create(
            user=self.user,
            address_line_1="Main Road",
            city="Surat",
            state="Gujarat",
            postal_code="395006",
        )

        self.assertTrue(
            customer.customer_id.startswith("CUST")
        )

        self.assertEqual(
            customer.city,
            "Surat",
        )

    def test_full_address(self):
        customer = Customer.objects.create(
            user=self.user,
            address_line_1="Ring Road",
            city="Ahmedabad",
            state="Gujarat",
            postal_code="380001",
        )

        self.assertIn(
            "Ahmedabad",
            customer.full_address,
        )