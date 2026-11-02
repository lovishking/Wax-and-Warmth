"""
Inventory Models — Stock tracking with transaction history.
"""

from django.db import models
from django.conf import settings


class Inventory(models.Model):
    """Tracks current stock levels for a product."""

    product = models.OneToOneField(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='inventory',
    )
    quantity = models.PositiveIntegerField(default=0, help_text='Total physical stock')
    reserved_quantity = models.PositiveIntegerField(default=0, help_text='Stock reserved for pending orders')
    reorder_level = models.PositiveIntegerField(default=5, help_text='Threshold for low-stock alert')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inventory'
        verbose_name_plural = 'Inventory'
        constraints = [
            models.CheckConstraint(
                check=models.Q(reserved_quantity__lte=models.F('quantity')),
                name='inventory_reserved_lte_quantity',
            ),
        ]

    def __str__(self):
        return f"{self.product.name} - Qty: {self.quantity}, Reserved: {self.reserved_quantity}"

    @property
    def available_quantity(self):
        """Available = total - reserved."""
        return max(0, self.quantity - self.reserved_quantity)

    @property
    def stock_status(self):
        """Return stock status string."""
        available = self.available_quantity
        if available <= 0:
            return 'OUT_OF_STOCK'
        elif available <= self.reorder_level:
            return 'LOW_STOCK'
        return 'IN_STOCK'

    @property
    def is_low_stock(self):
        return self.available_quantity <= self.reorder_level and self.available_quantity > 0

    @property
    def is_out_of_stock(self):
        return self.available_quantity <= 0


class InventoryTransaction(models.Model):
    """Records every stock modification for audit trail."""

    class TransactionType(models.TextChoices):
        PURCHASE = 'PURCHASE', 'Purchase'
        SALE = 'SALE', 'Sale'
        RESTOCK = 'RESTOCK', 'Restock'
        RETURN = 'RETURN', 'Return'
        ADJUSTMENT = 'ADJUSTMENT', 'Adjustment'
        RESERVATION = 'RESERVATION', 'Reservation'
        RELEASE = 'RELEASE', 'Release'

    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='inventory_transactions',
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices,
    )
    quantity = models.IntegerField(help_text='Quantity changed (positive or negative)')
    previous_quantity = models.PositiveIntegerField()
    new_quantity = models.PositiveIntegerField()
    previous_reserved = models.PositiveIntegerField(default=0)
    new_reserved = models.PositiveIntegerField(default=0)
    reason = models.TextField(blank=True)
    reference_id = models.CharField(
        max_length=100, blank=True,
        help_text='Order ID or other reference',
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inventory_transactions',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'inventory_transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', '-created_at']),
            models.Index(fields=['transaction_type']),
        ]
        constraints = [
            models.CheckConstraint(
                check=~models.Q(quantity=0),
                name='inventory_transaction_quantity_nonzero',
            ),
            models.CheckConstraint(
                check=models.Q(transaction_type__in=[
                    'PURCHASE', 'SALE', 'RESTOCK', 'RETURN', 'ADJUSTMENT',
                    'RESERVATION', 'RELEASE',
                ]),
                name='inventory_transaction_type_valid',
            ),
        ]

    def __str__(self):
        return (
            f"{self.get_transaction_type_display()} - {self.product.name}: "
            f"{self.previous_quantity} → {self.new_quantity}"
        )
