"""
Inventory Service Layer — Business logic with atomic transactions.
All inventory modifications go through this service to ensure consistency.
"""

from django.db import transaction
from django.core.exceptions import ValidationError

from .models import Inventory, InventoryTransaction


class InventoryService:
    """Handles all inventory operations with proper locking and transaction recording."""

    @staticmethod
    @transaction.atomic
    def restock(product, quantity, user=None, reason=''):
        """Add stock to a product. Creates a RESTOCK transaction."""
        if quantity <= 0:
            raise ValidationError('Restock quantity must be positive.')

        inventory = Inventory.objects.select_for_update().get(product=product)
        previous_qty = inventory.quantity

        inventory.quantity += quantity
        inventory.save()

        InventoryTransaction.objects.create(
            product=product,
            transaction_type=InventoryTransaction.TransactionType.RESTOCK,
            quantity=quantity,
            previous_quantity=previous_qty,
            new_quantity=inventory.quantity,
            previous_reserved=inventory.reserved_quantity,
            new_reserved=inventory.reserved_quantity,
            reason=reason or f'Restocked {quantity} units',
            created_by=user,
        )

        return inventory

    @staticmethod
    @transaction.atomic
    def adjust_stock(product, quantity, user=None, reason=''):
        """
        Adjust stock level. Quantity can be positive (add) or negative (remove).
        Creates an ADJUSTMENT transaction.
        """
        if quantity == 0:
            raise ValidationError('Stock adjustment must not be zero.')

        inventory = Inventory.objects.select_for_update().get(product=product)
        previous_qty = inventory.quantity
        new_qty = inventory.quantity + quantity

        if new_qty < 0:
            raise ValidationError(
                f'Cannot adjust stock below zero. Current: {inventory.quantity}, Adjustment: {quantity}'
            )

        if new_qty < inventory.reserved_quantity:
            raise ValidationError(
                f'Cannot adjust stock below reserved quantity ({inventory.reserved_quantity}).'
            )

        inventory.quantity = new_qty
        inventory.save()

        InventoryTransaction.objects.create(
            product=product,
            transaction_type=InventoryTransaction.TransactionType.ADJUSTMENT,
            quantity=quantity,
            previous_quantity=previous_qty,
            new_quantity=new_qty,
            previous_reserved=inventory.reserved_quantity,
            new_reserved=inventory.reserved_quantity,
            reason=reason or f'Stock adjusted by {quantity}',
            created_by=user,
        )

        return inventory

    @staticmethod
    @transaction.atomic
    def reserve_stock(product, quantity, user=None, reference_id=''):
        """
        Reserve stock for a pending order.
        available_stock → reserved_stock
        """
        if quantity <= 0:
            raise ValidationError('Reserve quantity must be positive.')

        inventory = Inventory.objects.select_for_update().get(product=product)
        available = inventory.available_quantity

        if quantity > available:
            raise ValidationError(
                f'Insufficient stock for {product.name}. '
                f'Only {available} units available.'
            )

        previous_reserved = inventory.reserved_quantity
        inventory.reserved_quantity += quantity
        inventory.save()

        InventoryTransaction.objects.create(
            product=product,
            transaction_type=InventoryTransaction.TransactionType.RESERVATION,
            quantity=quantity,
            previous_quantity=inventory.quantity,
            new_quantity=inventory.quantity,
            previous_reserved=previous_reserved,
            new_reserved=inventory.reserved_quantity,
            reference_id=reference_id,
            reason=f'Reserved {quantity} units for order',
            created_by=user,
        )

        return inventory

    @staticmethod
    @transaction.atomic
    def confirm_sale(product, quantity, user=None, reference_id=''):
        """
        Confirm a sale: reserved_stock → sold (deducted from both quantity and reserved).
        """
        if quantity <= 0:
            raise ValidationError('Sale quantity must be positive.')

        inventory = Inventory.objects.select_for_update().get(product=product)

        if quantity > inventory.reserved_quantity:
            raise ValidationError(
                f'Cannot confirm sale. Reserved: {inventory.reserved_quantity}, Requested: {quantity}'
            )

        previous_qty = inventory.quantity
        previous_reserved = inventory.reserved_quantity

        inventory.quantity -= quantity
        inventory.reserved_quantity -= quantity
        inventory.save()

        InventoryTransaction.objects.create(
            product=product,
            transaction_type=InventoryTransaction.TransactionType.SALE,
            quantity=-quantity,
            previous_quantity=previous_qty,
            new_quantity=inventory.quantity,
            previous_reserved=previous_reserved,
            new_reserved=inventory.reserved_quantity,
            reference_id=reference_id,
            reason=f'Sold {quantity} units',
            created_by=user,
        )

        return inventory

    @staticmethod
    @transaction.atomic
    def release_stock(product, quantity, user=None, reference_id=''):
        """
        Release reserved stock (e.g., on order cancellation).
        reserved_stock → available_stock
        """
        if quantity <= 0:
            raise ValidationError('Release quantity must be positive.')

        inventory = Inventory.objects.select_for_update().get(product=product)

        if quantity > inventory.reserved_quantity:
            raise ValidationError(
                f'Cannot release more than reserved. Reserved: {inventory.reserved_quantity}'
            )

        previous_reserved = inventory.reserved_quantity
        inventory.reserved_quantity -= quantity
        inventory.save()

        InventoryTransaction.objects.create(
            product=product,
            transaction_type=InventoryTransaction.TransactionType.RELEASE,
            quantity=quantity,
            previous_quantity=inventory.quantity,
            new_quantity=inventory.quantity,
            previous_reserved=previous_reserved,
            new_reserved=inventory.reserved_quantity,
            reference_id=reference_id,
            reason=f'Released {quantity} reserved units',
            created_by=user,
        )

        return inventory

    @staticmethod
    @transaction.atomic
    def process_return(product, quantity, user=None, reference_id=''):
        """
        Process a return: add stock back.
        sold_stock → available_stock
        """
        if quantity <= 0:
            raise ValidationError('Return quantity must be positive.')

        inventory = Inventory.objects.select_for_update().get(product=product)
        previous_qty = inventory.quantity

        inventory.quantity += quantity
        inventory.save()

        InventoryTransaction.objects.create(
            product=product,
            transaction_type=InventoryTransaction.TransactionType.RETURN,
            quantity=quantity,
            previous_quantity=previous_qty,
            new_quantity=inventory.quantity,
            previous_reserved=inventory.reserved_quantity,
            new_reserved=inventory.reserved_quantity,
            reference_id=reference_id,
            reason=f'Returned {quantity} units',
            created_by=user,
        )

        return inventory

    @staticmethod
    def check_availability(product, quantity):
        """Check if a product has sufficient available stock."""
        try:
            inventory = Inventory.objects.get(product=product)
            return inventory.available_quantity >= quantity
        except Inventory.DoesNotExist:
            return False

    @staticmethod
    def get_low_stock_products():
        """Get all products with low stock."""
        return Inventory.objects.select_related('product').filter(
            product__is_active=True,
            quantity__gt=0,
        ).extra(
            where=['quantity - reserved_quantity <= reorder_level AND quantity - reserved_quantity > 0']
        )

    @staticmethod
    def get_out_of_stock_products():
        """Get all out-of-stock products."""
        return Inventory.objects.select_related('product').filter(
            product__is_active=True,
        ).extra(
            where=['quantity - reserved_quantity <= 0']
        )
