"""
Product Serializers
"""

from rest_framework import serializers
from .models import Product, Category
from .services import FACET_FIELDS, parse_facet_values, set_product_facets


class ProductFacetTextField(serializers.CharField):
    """Keep the comma-separated API contract while storing facets relationally."""

    def to_internal_value(self, data):
        if isinstance(data, (list, tuple)):
            values = parse_facet_values(data)
        else:
            values = parse_facet_values(super().to_internal_value(data))
        if any(len(value) > 120 for value in values):
            raise serializers.ValidationError('Each value must be 120 characters or fewer.')
        normalized = ', '.join(values)
        if len(normalized) > 500:
            raise serializers.ValidationError('Combined values must be 500 characters or fewer.')
        return normalized


class CategorySerializer(serializers.ModelSerializer):
    """Full category serializer."""

    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'is_active', 'product_count']
        read_only_fields = ['id', 'slug']

    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer for product list (includes stock status)."""

    category_name = serializers.CharField(source='category.name', read_only=True, default=None)
    scent_notes = ProductFacetTextField(read_only=True)
    scent_notes_list = serializers.ListField(read_only=True)
    stock_status = serializers.SerializerMethodField()
    available_quantity = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'price',
            'category', 'category_name', 'scent_family',
            'scent_notes', 'scent_notes_list',
            'fragrance_strength', 'size', 'burn_time',
            'image', 'is_active', 'is_featured',
            'stock_status', 'available_quantity',
            'created_at',
        ]

    def get_stock_status(self, obj):
        try:
            inventory = obj.inventory
            available = inventory.available_quantity
            if available <= 0:
                return 'OUT_OF_STOCK'
            elif available <= inventory.reorder_level:
                return 'LOW_STOCK'
            return 'IN_STOCK'
        except Exception:
            return 'OUT_OF_STOCK'

    def get_available_quantity(self, obj):
        try:
            return obj.inventory.available_quantity
        except Exception:
            return 0


class ProductDetailSerializer(serializers.ModelSerializer):
    """Detailed product serializer with all fields."""

    category_name = serializers.CharField(source='category.name', read_only=True, default=None)
    scent_notes = ProductFacetTextField(read_only=True)
    mood = ProductFacetTextField(read_only=True)
    recommended_rooms = ProductFacetTextField(read_only=True)
    recommended_occasions = ProductFacetTextField(read_only=True)
    scent_notes_list = serializers.ListField(read_only=True)
    mood_list = serializers.ListField(read_only=True)
    rooms_list = serializers.ListField(read_only=True)
    occasions_list = serializers.ListField(read_only=True)
    stock_status = serializers.SerializerMethodField()
    available_quantity = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'price',
            'category', 'category_name', 'scent_family',
            'scent_notes', 'scent_notes_list',
            'fragrance_strength', 'size', 'burn_time',
            'mood', 'mood_list',
            'recommended_rooms', 'rooms_list',
            'recommended_occasions', 'occasions_list',
            'image', 'is_active', 'is_featured',
            'stock_status', 'available_quantity',
            'created_at', 'updated_at',
        ]

    def get_stock_status(self, obj):
        try:
            inventory = obj.inventory
            available = inventory.available_quantity
            if available <= 0:
                return 'OUT_OF_STOCK'
            elif available <= inventory.reorder_level:
                return 'LOW_STOCK'
            return 'IN_STOCK'
        except Exception:
            return 'OUT_OF_STOCK'

    def get_available_quantity(self, obj):
        try:
            return obj.inventory.available_quantity
        except Exception:
            return 0


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating products (admin)."""

    scent_notes = ProductFacetTextField(max_length=500)
    mood = ProductFacetTextField(max_length=500, required=False, allow_blank=True)
    recommended_rooms = ProductFacetTextField(max_length=500, required=False, allow_blank=True)
    recommended_occasions = ProductFacetTextField(max_length=500, required=False, allow_blank=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price',
            'category', 'scent_family', 'scent_notes',
            'fragrance_strength', 'size', 'burn_time',
            'mood', 'recommended_rooms', 'recommended_occasions',
            'image', 'is_active', 'is_featured',
        ]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError('Price must be greater than zero.')
        return value

    def create(self, validated_data):
        facets = {name: validated_data.pop(name) for name in FACET_FIELDS if name in validated_data}
        product = super().create(validated_data)
        set_product_facets(product, facets)
        return product

    def update(self, instance, validated_data):
        facets = {name: validated_data.pop(name) for name in FACET_FIELDS if name in validated_data}
        product = super().update(instance, validated_data)
        set_product_facets(product, facets)
        return product
