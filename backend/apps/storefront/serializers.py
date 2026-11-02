from rest_framework import serializers

from .models import SiteSettings


class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = ['site_name', 'site_description', 'contact_email', 'contact_phone', 'updated_at']
        read_only_fields = ['updated_at']
