from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.cart.models import Cart, CartItem
from apps.inventory.models import Inventory
from apps.products.models import Product

User = get_user_model()


def create_user(email, role=User.Role.CUSTOMER):
    return User.objects.create_user(
        email=email, username=email.split('@')[0], first_name='Buyer',
        password='Candle-River-928!Silver', role=role,
    )


class CartApiTests(APITestCase):
    def setUp(self):
        self.user = create_user('buyer@example.com')
        self.other = create_user('other@example.com')
        self.product = Product.objects.create(name='Test Candle', description='Test', price='10.00')
        self.inventory = self.product.inventory
        self.inventory.quantity = 5
        self.inventory.save(update_fields=['quantity'])

    def test_cart_requires_authentication(self):
        response = self.client.get('/api/cart/')
        self.assertEqual(response.status_code, 401)

    def test_add_update_remove_and_clear_cart(self):
        self.client.force_authenticate(user=self.user)
        added = self.client.post('/api/cart/add/', {'product_id': self.product.id, 'quantity': 2}, format='json')
        self.assertEqual(added.status_code, 200, added.data)
        self.assertEqual(added.data['data']['total_items'], 2)
        item = CartItem.objects.get(cart__user=self.user, product=self.product)

        updated = self.client.patch(f'/api/cart/items/{item.id}/', {'quantity': 3}, format='json')
        self.assertEqual(updated.status_code, 200, updated.data)
        invalid = self.client.patch(f'/api/cart/items/{item.id}/', {'quantity': 0}, format='json')
        self.assertEqual(invalid.status_code, 400)
        removed = self.client.delete(f'/api/cart/items/{item.id}/remove/')
        self.assertEqual(removed.status_code, 200, removed.data)
        self.client.post('/api/cart/add/', {'product_id': self.product.id, 'quantity': 1}, format='json')
        cleared = self.client.post('/api/cart/clear/', {}, format='json')
        self.assertEqual(cleared.status_code, 200, cleared.data)
        self.assertEqual(Cart.objects.get(user=self.user).items.count(), 0)

    def test_cart_cannot_exceed_available_inventory_or_edit_another_users_item(self):
        self.client.force_authenticate(user=self.user)
        no_stock = self.client.post('/api/cart/add/', {'product_id': self.product.id, 'quantity': 6}, format='json')
        self.assertEqual(no_stock.status_code, 400)
        self.client.post('/api/cart/add/', {'product_id': self.product.id, 'quantity': 1}, format='json')
        item = CartItem.objects.get(cart__user=self.user, product=self.product)
        self.client.force_authenticate(user=self.other)
        denied = self.client.patch(f'/api/cart/items/{item.id}/', {'quantity': 2}, format='json')
        self.assertEqual(denied.status_code, 404)
