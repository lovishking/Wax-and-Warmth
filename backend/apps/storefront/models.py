from django.core.exceptions import ValidationError
from django.db import models


class SiteSettings(models.Model):
    """Single editable set of the public storefront contact and identity details."""
    site_name = models.CharField(max_length=120, default='Wax and Warmth')
    site_description = models.TextField(blank=True, default='')
    contact_email = models.EmailField(default='realwaxandwarmth@gmail.com')
    contact_phone = models.CharField(max_length=40, default='+91 6200835077')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'site_settings'
        verbose_name = 'Site settings'
        verbose_name_plural = 'Site settings'
        constraints = [
            models.CheckConstraint(check=models.Q(id=1), name='site_settings_singleton_pk'),
        ]

    def save(self, *args, **kwargs):
        if self.pk not in (None, 1):
            raise ValidationError('Only one site settings record is allowed.')
        self.pk = 1
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.site_name
