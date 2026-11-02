"""
Chatbot Views — AI candle recommendation endpoint.
"""

from rest_framework import serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from apps.recommendations.services import RAGService


class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=1000, allow_blank=False, trim_whitespace=True)


class ChatView(APIView):
    """
    AI Candle Recommendation Chat endpoint.
    POST /api/chat/
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.validated_data['message']

        try:
            result = RAGService.get_recommendations(message)
            return Response({
                'success': True,
                'data': {
                    'message': result['message'],
                    'recommendations': result['recommendations'],
                },
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': {
                    'code': 'CHAT_ERROR',
                    'message': 'Sorry, I encountered an issue. Please try again.',
                },
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
