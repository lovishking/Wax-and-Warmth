"""Product signals — auto-create inventory on product creation."""

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product


@receiver(post_save, sender=Product)
def create_inventory_for_product(sender, instance, created, **kwargs):
    """Auto-create an inventory record when a product is created."""
    if created:
        from apps.inventory.models import Inventory
        Inventory.objects.get_or_create(
            product=instance,
            defaults={
                'quantity': 0,
                'reserved_quantity': 0,
                'reorder_level': 5,
            }
        )
