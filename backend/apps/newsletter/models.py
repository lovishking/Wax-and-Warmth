import uuid

from django.db import models
from django.db.models.functions import Lower


class NewsletterSubscription(models.Model):
    email = models.EmailField(unique=True)
    unsubscribe_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    is_active = models.BooleanField(default=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'newsletter_subscriptions'
        ordering = ['-subscribed_at']
        indexes = [models.Index(fields=['is_active', '-subscribed_at'])]
        constraints = [
            models.UniqueConstraint(Lower('email'), name='newsletter_email_ci_unique'),
        ]

    def __str__(self):
        return self.email
