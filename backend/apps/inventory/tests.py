from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.products.models import Product

User = get_user_model()


class InventoryApiTests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            email='buyer@example.com', username='buyer', first_name='Buyer',
            password='Candle-River-928!Silver',
        )
        self.admin = User.objects.create_user(
            email='admin@example.com', username='admin', first_name='Admin',
            password='Candle-River-928!Silver', role=User.Role.ADMIN,
        )
        self.product = Product.objects.create(name='Inventory Candle', description='Stock test', price='10.00')

    def test_inventory_list_and_restock_are_admin_only(self):
        self.client.force_authenticate(user=self.customer)
        denied = self.client.get('/api/inventory/')
        self.assertEqual(denied.status_code, 403)
        self.client.force_authenticate(user=self.admin)
        listed = self.client.get('/api/inventory/')
        self.assertEqual(listed.status_code, 200, listed.data)
        restocked = self.client.post('/api/inventory/restock/', {
            'product_id': self.product.id, 'quantity': 5, 'reason': 'stock setup',
        }, format='json')
        self.assertEqual(restocked.status_code, 200, restocked.data)
        self.product.inventory.refresh_from_db()
        self.assertEqual(self.product.inventory.quantity, 5)
