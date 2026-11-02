"""
Cart Views — Add, remove, update, clear.
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.products.models import Product
from apps.inventory.services import InventoryService
from .models import Cart, CartItem
from .serializers import CartSerializer, AddToCartSerializer, UpdateCartItemSerializer


class CartView(APIView):
    """Get current user's cart."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.prefetch_related(
            'items__product__category',
            'items__product__inventory',
        ).get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response({
            'success': True,
            'data': serializer.data,
        })


class AddToCartView(APIView):
    """Add a product to cart."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']

        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({
                'success': False,
                'error': {'code': 'PRODUCT_NOT_FOUND', 'message': 'Product not found.'},
            }, status=status.HTTP_404_NOT_FOUND)

        # Check stock availability
        if not InventoryService.check_availability(product, quantity):
            try:
                available = product.inventory.available_quantity
            except Exception:
                available = 0
            return Response({
                'success': False,
                'error': {
                    'code': 'INSUFFICIENT_STOCK',
                    'message': f'Only {available} units of {product.name} are available.',
                },
            }, status=status.HTTP_400_BAD_REQUEST)

        cart, _ = Cart.objects.get_or_create(user=request.user)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity},
        )

        if not created:
            cart_item.quantity += quantity
            # Re-check availability for total quantity
            if not InventoryService.check_availability(product, cart_item.quantity):
                return Response({
                    'success': False,
                    'error': {
                        'code': 'INSUFFICIENT_STOCK',
                        'message': f'Cannot add more. Only {product.inventory.available_quantity} units available.',
                    },
                }, status=status.HTTP_400_BAD_REQUEST)
            cart_item.save()

        cart.refresh_from_db()
        return Response({
            'success': True,
            'message': f'Added {quantity} x {product.name} to cart.',
            'data': CartSerializer(cart).data,
        })


class UpdateCartItemView(APIView):
    """Update cart item quantity."""

    permission_classes = [IsAuthenticated]

    def patch(self, request, item_id):
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            cart_item = CartItem.objects.select_related('product').get(
                id=item_id,
                cart__user=request.user,
            )
        except CartItem.DoesNotExist:
            return Response({
                'success': False,
                'error': {'code': 'ITEM_NOT_FOUND', 'message': 'Cart item not found.'},
            }, status=status.HTTP_404_NOT_FOUND)

        new_quantity = serializer.validated_data['quantity']

        if not InventoryService.check_availability(cart_item.product, new_quantity):
            return Response({
                'success': False,
                'error': {
                    'code': 'INSUFFICIENT_STOCK',
                    'message': f'Only {cart_item.product.inventory.available_quantity} units available.',
                },
            }, status=status.HTTP_400_BAD_REQUEST)

        cart_item.quantity = new_quantity
        cart_item.save()

        cart = cart_item.cart
        cart.refresh_from_db()
        return Response({
            'success': True,
            'message': 'Cart updated.',
            'data': CartSerializer(cart).data,
        })


class RemoveCartItemView(APIView):
    """Remove an item from cart."""

    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):
        try:
            cart_item = CartItem.objects.get(
                id=item_id,
                cart__user=request.user,
            )
        except CartItem.DoesNotExist:
            return Response({
                'success': False,
                'error': {'code': 'ITEM_NOT_FOUND', 'message': 'Cart item not found.'},
            }, status=status.HTTP_404_NOT_FOUND)

        cart = cart_item.cart
        cart_item.delete()
        cart.refresh_from_db()

        return Response({
            'success': True,
            'message': 'Item removed from cart.',
            'data': CartSerializer(cart).data,
        })


class ClearCartView(APIView):
    """Clear all items from cart."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
            cart.items.all().delete()
        except Cart.DoesNotExist:
            pass

        return Response({
            'success': True,
            'message': 'Cart cleared.',
        })
