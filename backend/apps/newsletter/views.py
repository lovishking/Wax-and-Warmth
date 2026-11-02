from django.db.models import Count, Q
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.users.permissions import IsAdminUser
from .models import NewsletterSubscription
from .serializers import (
    NewsletterSubscribeSerializer,
    NewsletterSubscriptionSerializer,
    NewsletterSubscriptionStatusSerializer,
    NewsletterUnsubscribeSerializer,
)


class SubscribeView(generics.CreateAPIView):
    serializer_class = NewsletterSubscribeSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'newsletter_subscribe'

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subscription = serializer.save()
        return Response({
            'success': True,
            'message': 'Thank you for subscribing to our newsletter.',
            'data': {'id': subscription.id, 'email': subscription.email},
        }, status=status.HTTP_201_CREATED)


class UnsubscribeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = NewsletterUnsubscribeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = NewsletterSubscription.objects.filter(
            unsubscribe_token=serializer.validated_data['token'],
            is_active=True,
        ).update(is_active=False)
        if not updated:
            return Response({
                'success': False,
                'error': {'code': 'SUBSCRIPTION_NOT_FOUND', 'message': 'Subscription not found or already inactive.'},
            }, status=status.HTTP_404_NOT_FOUND)
        return Response({'success': True, 'message': 'You have been unsubscribed.'})


class AdminSubscriptionListView(generics.ListAPIView):
    serializer_class = NewsletterSubscriptionSerializer
    permission_classes = [IsAdminUser]
    queryset = NewsletterSubscription.objects.all()
    filterset_fields = ['is_active']
    search_fields = ['email']
    ordering_fields = ['subscribed_at', 'email']
    ordering = ['-subscribed_at']


class AdminSubscriptionDetailView(generics.UpdateAPIView):
    serializer_class = NewsletterSubscriptionStatusSerializer
    permission_classes = [IsAdminUser]
    queryset = NewsletterSubscription.objects.all()
    http_method_names = ['patch', 'head', 'options']

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            'success': True,
            'message': 'Subscription status updated.',
            'data': NewsletterSubscriptionSerializer(instance).data,
        })


class AdminClearSubscriptionsView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request):
        deleted_count, _ = NewsletterSubscription.objects.all().delete()
        return Response({'success': True, 'data': {'deleted': deleted_count}})


class AdminNewsletterStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        counts = NewsletterSubscription.objects.aggregate(
            total=Count('id'), active=Count('id', filter=Q(is_active=True)),
        )
        return Response({'success': True, 'data': {
            'total': counts['total'],
            'active': counts['active'],
            'inactive': counts['total'] - counts['active'],
        }})
