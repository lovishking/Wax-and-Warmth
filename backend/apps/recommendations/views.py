"""
Recommendations Views — Admin endpoints for managing RAG data.
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.users.permissions import IsAdminUser
from apps.products.models import Product
from .services import RAGService


class UpdateKnowledgeView(APIView):
    """Update knowledge and embeddings for all products (admin only)."""

    permission_classes = [IsAdminUser]

    def post(self, request):
        try:
            count = RAGService.update_all_products()
            return Response({
                'success': True,
                'message': f'Updated knowledge for {count} products.',
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': {'code': 'UPDATE_FAILED', 'message': str(e)},
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateProductKnowledgeView(APIView):
    """Update knowledge for a specific product (admin only)."""

    permission_classes = [IsAdminUser]

    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({
                'success': False,
                'error': {'code': 'PRODUCT_NOT_FOUND', 'message': 'Product not found.'},
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            RAGService.update_product_knowledge(product)
            return Response({
                'success': True,
                'message': f'Updated knowledge for {product.name}.',
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': {'code': 'UPDATE_FAILED', 'message': str(e)},
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
