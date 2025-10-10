from django.db import models
from django.utils import timezone
from django.core.validators import EmailValidator


class NewsletterSubscription(models.Model):
    """Model to store newsletter email subscriptions."""
    
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        help_text="Email address of the subscriber"
    )
    subscribed_at = models.DateTimeField(
        default=timezone.now,
        help_text="Date and time when the user subscribed"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the subscription is active"
    )
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        help_text="IP address of the subscriber"
    )
    user_agent = models.TextField(
        blank=True,
        null=True,
        help_text="Browser information of the subscriber"
    )
    
    class Meta:
        verbose_name = "Newsletter Subscription"
        verbose_name_plural = "Newsletter Subscriptions"
        ordering = ['-subscribed_at']
    
    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"{self.email} ({status})"
    
    def deactivate(self):
        """Deactivate the subscription."""
        self.is_active = False
        self.save()
    
    def activate(self):
        """Activate the subscription."""
        self.is_active = True
        self.save()