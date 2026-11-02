"""
Order Service Layer — Business logic for order lifecycle.
"""

from django.db import transaction
from django.core.exceptions import ValidationError

from .models import Order, OrderItem
from apps.cart.models import Cart
from apps.inventory.services import InventoryService


class OrderService:
    """Handles order creation, cancellation, returns with proper inventory management."""

    @staticmethod
    @transaction.atomic
    def create_order_from_cart(user, shipping_address='', shipping_city='',
                                shipping_state='', shipping_pincode='', notes=''):
        """
        Create an order from the user's cart.
        1. Validate cart is not empty
        2. Reserve stock for each item
        3. Create order + order items with snapshotted prices
        4. Clear cart
        """
        try:
            cart = Cart.objects.prefetch_related('items__product__inventory').get(user=user)
        except Cart.DoesNotExist:
            raise ValidationError('Cart is empty.')

        cart_items = cart.items.all()
        if not cart_items.exists():
            raise ValidationError('Cart is empty.')

        # Validate stock availability for all items first
        for item in cart_items:
            if not item.product.is_active:
                raise ValidationError(f'{item.product.name} is no longer available.')
            if not InventoryService.check_availability(item.product, item.quantity):
                try:
                    available = item.product.inventory.available_quantity
                except Exception:
                    available = 0
                raise ValidationError(
                    f'Insufficient stock for {item.product.name}. '
                    f'Only {available} units available.'
                )

        # Calculate total from backend prices
        total_amount = sum(item.product.price * item.quantity for item in cart_items)

        # Create order
        order = Order.objects.create(
            user=user,
            total_amount=total_amount,
            status=Order.Status.PENDING,
            shipping_address=shipping_address,
            shipping_city=shipping_city,
            shipping_state=shipping_state,
            shipping_pincode=shipping_pincode,
            notes=notes,
        )

        # Create order items and reserve stock
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                quantity=item.quantity,
                unit_price=item.product.price,
            )
            # Reserve inventory
            InventoryService.reserve_stock(
                product=item.product,
                quantity=item.quantity,
                user=user,
                reference_id=str(order.id),
            )

        # Clear cart
        cart.items.all().delete()

        return order

    @staticmethod
    @transaction.atomic
    def confirm_order(order, user=None):
        """Confirm a pending order: reserved → sold."""
        if not order.can_transition_to('CONFIRMED'):
            raise ValidationError(
                f'Cannot confirm order in {order.status} status.'
            )

        for item in order.items.select_related('product').all():
            if not item.product_id:
                continue
            InventoryService.confirm_sale(
                product=item.product,
                quantity=item.quantity,
                user=user,
                reference_id=str(order.id),
            )

        order.status = Order.Status.CONFIRMED
        order.save()
        return order

    @staticmethod
    @transaction.atomic
    def cancel_order(order, user=None):
        """Cancel an order: release reserved stock."""
        if not order.can_transition_to('CANCELLED'):
            raise ValidationError(
                f'Cannot cancel order in {order.status} status.'
            )

        # Pending orders have reserved stock; confirmed and processing orders
        # have already deducted it, so cancellation must restore their units.
        if order.status == Order.Status.PENDING:
            for item in order.items.select_related('product').all():
                if not item.product_id:
                    continue
                InventoryService.release_stock(
                    product=item.product,
                    quantity=item.quantity,
                    user=user,
                    reference_id=str(order.id),
                )
        elif order.status in (Order.Status.CONFIRMED, Order.Status.PROCESSING):
            for item in order.items.select_related('product').all():
                if not item.product_id:
                    continue
                InventoryService.process_return(
                    product=item.product,
                    quantity=item.quantity,
                    user=user,
                    reference_id=str(order.id),
                )

        order.status = Order.Status.CANCELLED
        order.save()
        return order

    @staticmethod
    @transaction.atomic
    def update_status(order, new_status, user=None):
        """Update order status with validation."""
        if not order.can_transition_to(new_status):
            raise ValidationError(
                f'Invalid status transition: {order.status} → {new_status}'
            )

        if new_status == 'CONFIRMED':
            return OrderService.confirm_order(order, user)
        elif new_status == 'CANCELLED':
            return OrderService.cancel_order(order, user)
        elif new_status == 'RETURNED':
            return OrderService.process_return(order, user)

        order.status = new_status
        order.save()
        return order

    @staticmethod
    @transaction.atomic
    def process_return(order, user=None):
        """Process a return: add stock back."""
        if not order.can_transition_to('RETURNED'):
            raise ValidationError(
                f'Cannot return order in {order.status} status.'
            )

        for item in order.items.select_related('product').all():
            if not item.product_id:
                continue
            InventoryService.process_return(
                product=item.product,
                quantity=item.quantity,
                user=user,
                reference_id=str(order.id),
            )

        order.status = Order.Status.RETURNED
        order.save()
        return order
