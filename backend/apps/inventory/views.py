"""
Inventory Views — Admin endpoints for stock management.
"""

from rest_framework import generics, status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.users.permissions import IsAdminUser
from apps.products.models import Product
from .models import Inventory, InventoryTransaction
from .serializers import (
    InventorySerializer,
    InventoryTransactionSerializer,
    RestockSerializer,
    AdjustStockSerializer,
    SetReorderLevelSerializer,
)
from .services import InventoryService


class InventoryListView(generics.ListAPIView):
    """List all inventory items (admin only)."""

    serializer_class = InventorySerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Inventory.objects.select_related('product').order_by('product__name', 'pk')


class InventoryDetailView(generics.RetrieveAPIView):
    """Get inventory for a specific product (admin only)."""

    serializer_class = InventorySerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Inventory.objects.select_related('product').all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'data': serializer.data,
        })


class RestockView(APIView):
    """Restock a product (admin only)."""

    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = RestockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            product = Product.objects.get(id=serializer.validated_data['product_id'])
        except Product.DoesNotExist:
            return Response({
                'success': False,
                'error': {'code': 'PRODUCT_NOT_FOUND', 'message': 'Product not found.'},
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            inventory = InventoryService.restock(
                product=product,
                quantity=serializer.validated_data['quantity'],
                user=request.user,
                reason=serializer.validated_data.get('reason', ''),
            )
            return Response({
                'success': True,
                'message': f'Restocked {serializer.validated_data["quantity"]} units of {product.name}.',
                'data': InventorySerializer(inventory).data,
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': {'code': 'RESTOCK_FAILED', 'message': str(e)},
            }, status=status.HTTP_400_BAD_REQUEST)


class AdjustStockView(APIView):
    """Adjust stock levels (admin only)."""

    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = AdjustStockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            product = Product.objects.get(id=serializer.validated_data['product_id'])
        except Product.DoesNotExist:
            return Response({
                'success': False,
                'error': {'code': 'PRODUCT_NOT_FOUND', 'message': 'Product not found.'},
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            inventory = InventoryService.adjust_stock(
                product=product,
                quantity=serializer.validated_data['quantity'],
                user=request.user,
                reason=serializer.validated_data.get('reason', ''),
            )
            return Response({
                'success': True,
                'message': f'Stock adjusted for {product.name}.',
                'data': InventorySerializer(inventory).data,
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': {'code': 'ADJUSTMENT_FAILED', 'message': str(e)},
            }, status=status.HTTP_400_BAD_REQUEST)


class SetReorderLevelView(APIView):
    """Set reorder level for a product (admin only)."""

    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = SetReorderLevelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            inventory = Inventory.objects.get(
                product_id=serializer.validated_data['product_id']
            )
        except Inventory.DoesNotExist:
            return Response({
                'success': False,
                'error': {'code': 'INVENTORY_NOT_FOUND', 'message': 'Inventory record not found.'},
            }, status=status.HTTP_404_NOT_FOUND)

        inventory.reorder_level = serializer.validated_data['reorder_level']
        inventory.save()

        return Response({
            'success': True,
            'message': f'Reorder level set to {inventory.reorder_level}.',
            'data': InventorySerializer(inventory).data,
        })


class LowStockView(generics.ListAPIView):
    """List low-stock products (admin only)."""

    serializer_class = InventorySerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Inventory.objects.select_related('product').filter(
            product__is_active=True,
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        low_stock = [inv for inv in queryset if inv.is_low_stock]
        serializer = self.get_serializer(low_stock, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
        })


class OutOfStockView(generics.ListAPIView):
    """List out-of-stock products (admin only)."""

    serializer_class = InventorySerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Inventory.objects.select_related('product').filter(
            product__is_active=True,
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        out_of_stock = [inv for inv in queryset if inv.is_out_of_stock]
        serializer = self.get_serializer(out_of_stock, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
        })


class InventoryTransactionListView(generics.ListAPIView):
    """List inventory transactions (admin only)."""

    serializer_class = InventoryTransactionSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = InventoryTransaction.objects.select_related('product', 'created_by')
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        transaction_type = self.request.query_params.get('type')
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type.upper())
        return queryset


class DashboardStatsView(APIView):
    """Dashboard statistics (admin only)."""

    permission_classes = [IsAdminUser]

    def get(self, request):
        from apps.orders.models import Order

        total_products = Product.objects.filter(is_active=True).count()
        total_inventory = sum(
            inv.quantity for inv in Inventory.objects.all()
        )
        inventories = list(Inventory.objects.select_related('product').filter(
            product__is_active=True
        ))
        low_stock_count = sum(1 for inv in inventories if inv.is_low_stock)
        out_of_stock_count = sum(1 for inv in inventories if inv.is_out_of_stock)

        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(status='PENDING').count()
        completed_orders = Order.objects.filter(status='DELIVERED').count()

        from django.db.models import Sum
        revenue = Order.objects.filter(
            status__in=['CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED']
        ).aggregate(total=Sum('total_amount'))['total'] or 0

        return Response({
            'success': True,
            'data': {
                'total_products': total_products,
                'total_inventory': total_inventory,
                'low_stock': low_stock_count,
                'out_of_stock': out_of_stock_count,
                'total_orders': total_orders,
                'pending_orders': pending_orders,
                'completed_orders': completed_orders,
                'revenue': float(revenue),
            },
        })
