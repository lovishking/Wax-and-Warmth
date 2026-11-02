"""
Inventory Serializers
"""

from rest_framework import serializers
from .models import Inventory, InventoryTransaction


class InventorySerializer(serializers.ModelSerializer):
    """Inventory display serializer."""

    product_name = serializers.CharField(source='product.name', read_only=True)
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    available_quantity = serializers.IntegerField(read_only=True)
    stock_status = serializers.CharField(read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    is_out_of_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Inventory
        fields = [
            'id', 'product_id', 'product_name', 'quantity',
            'reserved_quantity', 'available_quantity', 'reorder_level',
            'stock_status', 'is_low_stock', 'is_out_of_stock',
            'updated_at',
        ]


class InventoryTransactionSerializer(serializers.ModelSerializer):
    """Transaction history serializer."""

    product_name = serializers.CharField(source='product.name', read_only=True)
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = InventoryTransaction
        fields = [
            'id', 'product', 'product_name', 'transaction_type',
            'quantity', 'previous_quantity', 'new_quantity',
            'previous_reserved', 'new_reserved',
            'reason', 'reference_id',
            'created_by', 'created_by_name', 'created_at',
        ]

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username
        return 'System'


class RestockSerializer(serializers.Serializer):
    """Serializer for restock requests."""

    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    reason = serializers.CharField(required=False, default='')


class AdjustStockSerializer(serializers.Serializer):
    """Serializer for stock adjustment requests."""

    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField()
    reason = serializers.CharField(required=False, default='')


class SetReorderLevelSerializer(serializers.Serializer):
    """Serializer for setting reorder level."""

    product_id = serializers.IntegerField()
    reorder_level = serializers.IntegerField(min_value=0)
