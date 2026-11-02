"""
Product Views — CRUD, search, filtering.
"""

from rest_framework import viewsets, generics, status, filters
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from apps.users.permissions import IsAdminUser
from .models import Product, Category
from .serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    ProductCreateUpdateSerializer,
    CategorySerializer,
)
from .filters import ProductFilter


class CategoryViewSet(viewsets.ModelViewSet):
    """Category CRUD operations."""

    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]


class ProductViewSet(viewsets.ModelViewSet):
    """Product CRUD with search and filtering."""

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = [
        'name', 'description', 'scent_family',
        'facet_assignments__facet__value',
    ]
    ordering_fields = ['price', 'name', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Product.objects.select_related('category').prefetch_related(
            'inventory', 'facet_assignments__facet',
        )
        # Non-admin users only see active products
        if not (self.request.user.is_authenticated and
                (self.request.user.role == 'ADMIN' or self.request.user.is_superuser)):
            queryset = queryset.filter(is_active=True)
        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        elif self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductCreateUpdateSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'featured']:
            return [AllowAny()]
        return [IsAdminUser()]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'data': serializer.data,
        })

    def perform_destroy(self, instance):
        # Archive catalog entries so historic inventory transactions remain valid.
        instance.is_active = False
        instance.save(update_fields=['is_active', 'updated_at'])

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
        })

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def featured(self, request):
        """Get featured products."""
        queryset = self.get_queryset().filter(is_featured=True)[:8]
        serializer = ProductListSerializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
        })
