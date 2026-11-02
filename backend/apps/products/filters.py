"""
Product Filters
"""

import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    """Filter products by various criteria."""

    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    category = django_filters.NumberFilter(field_name='category__id')
    category_slug = django_filters.CharFilter(field_name='category__slug')
    scent_family = django_filters.CharFilter(field_name='scent_family', lookup_expr='iexact')
    fragrance_strength = django_filters.CharFilter(field_name='fragrance_strength', lookup_expr='iexact')
    size = django_filters.CharFilter(field_name='size', lookup_expr='iexact')
    is_featured = django_filters.BooleanFilter(field_name='is_featured')
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')
    scent_note = django_filters.CharFilter(method='filter_facet')
    mood = django_filters.CharFilter(method='filter_facet')
    room = django_filters.CharFilter(method='filter_facet')
    occasion = django_filters.CharFilter(method='filter_facet')

    class Meta:
        model = Product
        fields = [
            'category', 'category_slug', 'scent_family',
            'fragrance_strength', 'size', 'is_featured',
            'min_price', 'max_price', 'in_stock',
            'scent_note', 'mood', 'room', 'occasion',
        ]

    def filter_facet(self, queryset, name, value):
        kind = {
            'scent_note': 'SCENT_NOTE',
            'mood': 'MOOD',
            'room': 'ROOM',
            'occasion': 'OCCASION',
        }[name]
        return queryset.filter(
            facet_assignments__facet__kind=kind,
            facet_assignments__facet__normalized_value=value.strip().casefold(),
        ).distinct()

    def filter_in_stock(self, queryset, name, value):
        """Filter by stock availability."""
        if value:
            return queryset.filter(
                inventory__quantity__gt=0
            ).filter(
                inventory__quantity__gt=models.F('inventory__reserved_quantity')
            )
        return queryset


# Need to import models for F expression
from django.db import models  # noqa: E402
