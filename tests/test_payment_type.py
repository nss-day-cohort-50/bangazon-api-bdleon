from faker import Faker
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.core.management import call_command
from django.contrib.auth.models import User

from bangazon_api.models import payment_type, PaymentType


class PaymentTests(APITestCase):
    def setUp(self):
        """
        Seed the database
        """
        call_command('seed_db', user_count=2)
        self.user1 = User.objects.filter(store=None).first()
        self.token = Token.objects.get(user=self.user1)

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.token.key}')

        self.faker = Faker()

        payment_type = {
            "merchant": "Discover",
            "acctNumber": "123344566",
            "customer": 1
        }

        response = self.client.post(
            f'/api/payment-types', payment_type, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_payment_type(self):
        """
        Ensure we can add a payment type for a customer.
        """
        # Add product to order
        data = {
            "merchant": self.faker.credit_card_provider(),
            "acctNumber": self.faker.credit_card_number()
        }

        response = self.client.post('/api/payment-types', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.data['id'])
        self.assertEqual(response.data["merchant_name"], data['merchant'])
        self.assertEqual(response.data["acct_number"], data['acctNumber'])

    def test_delete_payment_type(self):
        """
       Ensure we can delete a paymentType.
       """
        payment_type = PaymentType.objects.first()
        data = {
            "merchant_name": payment_type.merchant_name,
            "acct_number": payment_type.acct_number,
            "customer": payment_type.customer

        }
        response = self.client.delete(
            f'/api/payment-types/{payment_type.id}', data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.delete(f'/api/payment-types/{payment_type.id}')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
