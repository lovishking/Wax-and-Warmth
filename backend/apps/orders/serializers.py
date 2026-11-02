"""
Order Serializers
"""

from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    """Order item serializer."""

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'unit_price', 'subtotal']


class OrderSerializer(serializers.ModelSerializer):
    """Order serializer with items."""

    items = OrderItemSerializer(many=True, read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'user_email', 'total_amount', 'status',
            'shipping_address', 'shipping_city', 'shipping_state',
            'shipping_pincode', 'notes', 'items',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'total_amount', 'status', 'created_at', 'updated_at']


class OrderListSerializer(serializers.ModelSerializer):
    """Lighter serializer for order lists."""

    item_count = serializers.SerializerMethodField()
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'user_email', 'total_amount', 'status',
            'item_count', 'created_at', 'updated_at',
        ]

    def get_item_count(self, obj):
        return obj.items.count()


class CreateOrderSerializer(serializers.Serializer):
    """Serializer for creating an order from cart."""

    shipping_address = serializers.CharField(max_length=500)
    shipping_city = serializers.CharField(max_length=100)
    shipping_state = serializers.CharField(max_length=100)
    shipping_pincode = serializers.RegexField(r'^\d{6}$', max_length=6)
    notes = serializers.CharField(required=False, default='')


class UpdateOrderStatusSerializer(serializers.Serializer):
    """Serializer for updating order status."""

    status = serializers.ChoiceField(choices=Order.Status.choices)
