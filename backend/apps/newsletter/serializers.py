from django.db import IntegrityError, transaction
from rest_framework import serializers

from .models import NewsletterSubscription


class NewsletterSubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterSubscription
        fields = ['email']
        extra_kwargs = {'email': {'validators': []}}

    def validate_email(self, value):
        email = value.strip().casefold()
        subscription = NewsletterSubscription.objects.filter(email__iexact=email).first()
        if subscription and subscription.is_active:
            raise serializers.ValidationError('This email is already subscribed.')
        self.existing_subscription = subscription
        return email

    def create(self, validated_data):
        request = self.context.get('request')
        ip_address = request.META.get('REMOTE_ADDR') if request else None
        user_agent = request.META.get('HTTP_USER_AGENT', '') if request else ''
        if self.existing_subscription:
            subscription = self.existing_subscription
            subscription.is_active = True
            subscription.ip_address = ip_address
            subscription.user_agent = user_agent
            subscription.save(update_fields=['is_active', 'ip_address', 'user_agent', 'updated_at'])
            return subscription
        try:
            with transaction.atomic():
                return NewsletterSubscription.objects.create(
                    **validated_data,
                    ip_address=ip_address,
                    user_agent=user_agent,
                )
        except IntegrityError:
            raise serializers.ValidationError({'email': 'This email is already subscribed.'})


class NewsletterSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterSubscription
        fields = ['id', 'email', 'is_active', 'subscribed_at', 'updated_at']


class NewsletterSubscriptionStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterSubscription
        fields = ['is_active']


class NewsletterUnsubscribeSerializer(serializers.Serializer):
    token = serializers.UUIDField()
