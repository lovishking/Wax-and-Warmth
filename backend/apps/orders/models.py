"""
Order Models — Order with items and status tracking.
"""

from django.db import models
from django.conf import settings


class Order(models.Model):
    """Customer order."""

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        PROCESSING = 'PROCESSING', 'Processing'
        SHIPPED = 'SHIPPED', 'Shipped'
        DELIVERED = 'DELIVERED', 'Delivered'
        CANCELLED = 'CANCELLED', 'Cancelled'
        RETURNED = 'RETURNED', 'Returned'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='orders',
    )
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    shipping_address = models.TextField(blank=True)
    shipping_city = models.CharField(max_length=100, blank=True)
    shipping_state = models.CharField(max_length=100, blank=True)
    shipping_pincode = models.CharField(max_length=10, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
        ]
        constraints = [
            models.CheckConstraint(check=models.Q(total_amount__gte=0), name='order_total_nonnegative'),
            models.CheckConstraint(
                check=models.Q(status__in=[
                    'PENDING', 'CONFIRMED', 'PROCESSING', 'SHIPPED',
                    'DELIVERED', 'CANCELLED', 'RETURNED',
                ]),
                name='order_status_valid',
            ),
        ]

    def __str__(self):
        return f"Order #{self.id} - {self.user.email} - {self.status}"

    # Valid status transitions
    VALID_TRANSITIONS = {
        'PENDING': ['CONFIRMED', 'CANCELLED'],
        'CONFIRMED': ['PROCESSING', 'CANCELLED'],
        'PROCESSING': ['SHIPPED', 'CANCELLED'],
        'SHIPPED': ['DELIVERED'],
        'DELIVERED': ['RETURNED'],
        'CANCELLED': [],
        'RETURNED': [],
    }

    def can_transition_to(self, new_status):
        """Check if a status transition is valid."""
        return new_status in self.VALID_TRANSITIONS.get(self.status, [])


class OrderItem(models.Model):
    """Individual item in an order. Price is snapshotted at purchase time."""

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.SET_NULL,
        null=True,
        related_name='order_items',
    )
    product_name = models.CharField(max_length=200, help_text='Snapshot of product name')
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text='Price at time of purchase',
    )

    class Meta:
        db_table = 'order_items'
        constraints = [
            models.CheckConstraint(check=models.Q(quantity__gt=0), name='order_item_quantity_positive'),
            models.CheckConstraint(check=models.Q(unit_price__gt=0), name='order_item_price_positive'),
            models.UniqueConstraint(fields=['order', 'product'], name='order_item_product_uniq'),
        ]

    def __str__(self):
        return f"{self.product_name} x {self.quantity} = ₹{self.subtotal}"

    @property
    def subtotal(self):
        return self.unit_price * self.quantity
