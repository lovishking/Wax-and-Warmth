from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.cart.models import Cart, CartItem
from apps.inventory.models import Inventory
from apps.orders.models import Order
from apps.inventory.models import InventoryTransaction
from apps.products.models import Product

User = get_user_model()


def create_user(email, role=User.Role.CUSTOMER):
    return User.objects.create_user(
        email=email, username=email.split('@')[0], first_name='Buyer',
        password='Candle-River-928!Silver', role=role,
    )


class InventoryAndOrderApiTests(APITestCase):
    def setUp(self):
        self.customer = create_user('buyer@example.com')
        self.other = create_user('other@example.com')
        self.admin = create_user('admin@example.com', User.Role.ADMIN)
        self.product = Product.objects.create(name='Order Candle', description='Order test', price='12.50')
        self.inventory = self.product.inventory

    def test_inventory_mutations_are_admin_only(self):
        payload = {'product_id': self.product.id, 'quantity': 5, 'reason': 'test stock'}
        self.client.force_authenticate(user=self.customer)
        denied = self.client.post('/api/inventory/restock/', payload, format='json')
        self.assertEqual(denied.status_code, 403)
        self.client.force_authenticate(user=self.admin)
        restocked = self.client.post('/api/inventory/restock/', payload, format='json')
        self.assertEqual(restocked.status_code, 200, restocked.data)
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 5)

    def test_order_uses_server_prices_reserves_stock_and_clears_cart(self):
        self.inventory.quantity = 5
        self.inventory.save(update_fields=['quantity'])
        cart, _ = Cart.objects.get_or_create(user=self.customer)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        self.client.force_authenticate(user=self.customer)
        response = self.client.post('/api/orders/create/', {
            'shipping_address': '14 Market Road', 'shipping_city': 'Dhanbad',
            'shipping_state': 'Jharkhand', 'shipping_pincode': '826001', 'notes': 'Call first',
        }, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        order_data = response.data['data']
        order = Order.objects.get(pk=order_data['id'])
        self.assertEqual(order.total_amount, Decimal('25.00'))
        self.assertEqual(order.items.get().subtotal, Decimal('25.00'))
        self.assertEqual(order.items.get().product_name, 'Order Candle')
        self.assertEqual(cart.items.count(), 0)
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.reserved_quantity, 2)

        self.client.force_authenticate(user=self.other)
        forbidden = self.client.get(f'/api/orders/{order.id}/')
        self.assertEqual(forbidden.status_code, 404)
        self.client.force_authenticate(user=self.customer)
        mine = self.client.get('/api/orders/')
        self.assertEqual(mine.status_code, 200)
        self.assertEqual(mine.data['results'][0]['id'], order.id)

    def test_invalid_shipping_postal_code_and_empty_order_are_rejected(self):
        self.client.force_authenticate(user=self.customer)
        payload = {
            'shipping_address': '14 Market Road', 'shipping_city': 'Dhanbad',
            'shipping_state': 'Jharkhand', 'shipping_pincode': '12AB',
        }
        invalid = self.client.post('/api/orders/create/', payload, format='json')
        self.assertEqual(invalid.status_code, 400)
        self.assertEqual(Order.objects.count(), 0)
        payload['shipping_pincode'] = '826001'
        empty = self.client.post('/api/orders/create/', payload, format='json')
        self.assertEqual(empty.status_code, 400)
        self.assertEqual(Order.objects.count(), 0)

    def test_confirmation_and_cancellation_persist_inventory_transactions(self):
        self.inventory.quantity = 5
        self.inventory.save(update_fields=['quantity'])
        cart, _ = Cart.objects.get_or_create(user=self.customer)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        self.client.force_authenticate(user=self.customer)
        created = self.client.post('/api/orders/create/', {
            'shipping_address': '14 Market Road', 'shipping_city': 'Dhanbad',
            'shipping_state': 'Jharkhand', 'shipping_pincode': '826001',
        }, format='json')
        self.assertEqual(created.status_code, 201, created.data)
        order = Order.objects.get(pk=created.data['data']['id'])

        self.client.force_authenticate(user=self.admin)
        confirmed = self.client.patch(f'/api/orders/admin/{order.id}/status/', {
            'status': 'CONFIRMED',
        }, format='json')
        self.assertEqual(confirmed.status_code, 200, confirmed.data)
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 3)
        self.assertEqual(self.inventory.reserved_quantity, 0)
        self.assertTrue(InventoryTransaction.objects.filter(
            product=self.product,
            transaction_type=InventoryTransaction.TransactionType.SALE,
            reference_id=str(order.id),
            quantity=-2,
        ).exists())

        cancelled = self.client.post(f'/api/orders/{order.id}/cancel/')
        self.assertEqual(cancelled.status_code, 200, cancelled.data)
        self.inventory.refresh_from_db()
        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.CANCELLED)
        self.assertEqual(self.inventory.quantity, 5)
        self.assertEqual(self.inventory.reserved_quantity, 0)

    def test_customer_can_cancel_pending_order_and_release_reservation(self):
        self.inventory.quantity = 3
        self.inventory.save(update_fields=['quantity'])
        cart, _ = Cart.objects.get_or_create(user=self.customer)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        self.client.force_authenticate(user=self.customer)
        created = self.client.post('/api/orders/create/', {
            'shipping_address': '14 Market Road', 'shipping_city': 'Dhanbad',
            'shipping_state': 'Jharkhand', 'shipping_pincode': '826001',
        }, format='json')
        self.assertEqual(created.status_code, 201, created.data)
        order_id = created.data['data']['id']

        cancelled = self.client.post(f'/api/orders/{order_id}/cancel/')
        self.assertEqual(cancelled.status_code, 200, cancelled.data)
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 3)
        self.assertEqual(self.inventory.reserved_quantity, 0)
        self.assertTrue(InventoryTransaction.objects.filter(
            product=self.product,
            transaction_type=InventoryTransaction.TransactionType.RELEASE,
            reference_id=str(order_id),
            quantity=2,
        ).exists())
