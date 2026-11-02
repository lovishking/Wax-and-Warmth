"""
Order Views — Order creation, listing, and management.
"""

from decimal import Decimal

from django.db.models import Count, DecimalField, ExpressionWrapper, F, Sum
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.users.permissions import IsAdminUser, IsOwnerOrAdmin
from .models import Order, OrderItem
from .serializers import (
    OrderSerializer,
    OrderListSerializer,
    CreateOrderSerializer,
    UpdateOrderStatusSerializer,
)
from .services import OrderService


class CreateOrderView(APIView):
    """Create order from cart (customer)."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            order = OrderService.create_order_from_cart(
                user=request.user,
                **serializer.validated_data,
            )
            return Response({
                'success': True,
                'message': 'Order placed successfully.',
                'data': OrderSerializer(order).data,
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'success': False,
                'error': {'code': 'ORDER_FAILED', 'message': str(e)},
            }, status=status.HTTP_400_BAD_REQUEST)


class MyOrdersView(generics.ListAPIView):
    """List current user's orders."""

    serializer_class = OrderListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')


class OrderDetailView(generics.RetrieveAPIView):
    """Get order details (owner or admin)."""

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN' or user.is_superuser:
            return Order.objects.all().prefetch_related('items')
        return Order.objects.filter(user=user).prefetch_related('items')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'data': serializer.data,
        })


class CancelOrderView(APIView):
    """Cancel an order (owner or admin)."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({
                'success': False,
                'error': {'code': 'ORDER_NOT_FOUND', 'message': 'Order not found.'},
            }, status=status.HTTP_404_NOT_FOUND)

        # Check ownership or admin
        if order.user != request.user and not (
            request.user.role == 'ADMIN' or request.user.is_superuser
        ):
            return Response({
                'success': False,
                'error': {'code': 'UNAUTHORIZED', 'message': 'Not authorized.'},
            }, status=status.HTTP_403_FORBIDDEN)

        try:
            order = OrderService.cancel_order(order, user=request.user)
            return Response({
                'success': True,
                'message': 'Order cancelled.',
                'data': OrderSerializer(order).data,
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': {'code': 'CANCEL_FAILED', 'message': str(e)},
            }, status=status.HTTP_400_BAD_REQUEST)


# ── Admin endpoints ──

class AdminOrderListView(generics.ListAPIView):
    """List all orders (admin only)."""

    serializer_class = OrderListSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = Order.objects.all().prefetch_related('items')
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter.upper())
        return queryset


class AdminSalesView(APIView):
    """Return paid sales, unpaid WhatsApp orders, and product-level units sold."""

    permission_classes = [IsAdminUser]

    def get(self, request):
        paid_statuses = [
            Order.Status.CONFIRMED,
            Order.Status.PROCESSING,
            Order.Status.SHIPPED,
            Order.Status.DELIVERED,
        ]
        paid_orders = Order.objects.filter(status__in=paid_statuses)
        pending_orders = Order.objects.filter(status=Order.Status.PENDING)

        paid_revenue = paid_orders.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        pending_revenue = pending_orders.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        line_revenue = ExpressionWrapper(
            F('quantity') * F('unit_price'),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        )
        products = OrderItem.objects.filter(order__status__in=paid_statuses).values(
            'product_id', 'product_name',
        ).annotate(
            units_sold=Sum('quantity'),
            order_count=Count('order_id', distinct=True),
            revenue=Sum(line_revenue),
        ).order_by('-units_sold', '-revenue', 'product_name')

        recent_orders = []
        for order in Order.objects.select_related('user').prefetch_related('items')[:50]:
            recent_orders.append({
                'id': order.id,
                'customer': order.user.email,
                'status': order.status,
                'total_amount': order.total_amount,
                'created_at': order.created_at,
                'items': [
                    {'name': item.product_name, 'quantity': item.quantity}
                    for item in order.items.all()
                ],
            })

        return Response({
            'success': True,
            'data': {
                'summary': {
                    'paid_revenue': paid_revenue,
                    'units_sold': OrderItem.objects.filter(
                        order__status__in=paid_statuses,
                    ).aggregate(total=Sum('quantity'))['total'] or 0,
                    'paid_orders': paid_orders.count(),
                    'pending_orders': pending_orders.count(),
                    'pending_revenue': pending_revenue,
                },
                'products': list(products),
                'orders': recent_orders,
            },
        })


class AdminUpdateOrderStatusView(APIView):
    """Update order status (admin only)."""

    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        serializer = UpdateOrderStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({
                'success': False,
                'error': {'code': 'ORDER_NOT_FOUND', 'message': 'Order not found.'},
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            order = OrderService.update_status(
                order,
                serializer.validated_data['status'],
                user=request.user,
            )
            return Response({
                'success': True,
                'message': f'Order status updated to {order.status}.',
                'data': OrderSerializer(order).data,
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': {'code': 'STATUS_UPDATE_FAILED', 'message': str(e)},
            }, status=status.HTTP_400_BAD_REQUEST)
