from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import NewsletterSubscription


@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    """Admin interface for newsletter subscriptions."""
    
    list_display = [
        'email',
        'is_active_display',
        'subscribed_at',
        'ip_address',
        'actions_column'
    ]
    
    list_filter = [
        'is_active',
        'subscribed_at',
    ]
    
    search_fields = [
        'email',
        'ip_address',
    ]
    
    readonly_fields = [
        'subscribed_at',
        'ip_address',
        'user_agent',
    ]
    
    list_per_page = 50
    
    ordering = ['-subscribed_at']
    
    fieldsets = (
        ('Subscription Information', {
            'fields': ('email', 'is_active')
        }),
        ('Metadata', {
            'fields': ('subscribed_at', 'ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )
    
    def is_active_display(self, obj):
        """Display active status with colored indicator."""
        if obj.is_active:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Active</span>'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">✗ Inactive</span>'
            )
    is_active_display.short_description = 'Status'
    is_active_display.admin_order_field = 'is_active'
    
    def actions_column(self, obj):
        """Display action buttons for each subscription."""
        if obj.is_active:
            return format_html(
                '<a class="button" href="#" onclick="return confirm(\'Deactivate this subscription?\') && '
                'fetch(\'/admin/newsletter/newslettersubscription/{}/deactivate/\', {{method: \'POST\', '
                'headers: {{\'X-CSRFToken\': document.querySelector(\'[name=csrfmiddlewaretoken]\').value}}}}).then(() => location.reload())">Deactivate</a>',
                obj.pk
            )
        else:
            return format_html(
                '<a class="button" href="#" onclick="return confirm(\'Activate this subscription?\') && '
                'fetch(\'/admin/newsletter/newslettersubscription/{}/activate/\', {{method: \'POST\', '
                'headers: {{\'X-CSRFToken\': document.querySelector(\'[name=csrfmiddlewaretoken]\').value}}}}).then(() => location.reload())">Activate</a>',
                obj.pk
            )
    actions_column.short_description = 'Actions'
    
    def get_queryset(self, request):
        """Optimize database queries."""
        queryset = super().get_queryset(request)
        return queryset.select_related()
    
    def changelist_view(self, request, extra_context=None):
        """Add summary statistics to the changelist view."""
        extra_context = extra_context or {}
        
        # Calculate statistics
        total_subscriptions = NewsletterSubscription.objects.count()
        active_subscriptions = NewsletterSubscription.objects.filter(is_active=True).count()
        inactive_subscriptions = NewsletterSubscription.objects.filter(is_active=False).count()
        
        extra_context['summary_stats'] = {
            'total': total_subscriptions,
            'active': active_subscriptions,
            'inactive': inactive_subscriptions,
        }
        
        return super().changelist_view(request, extra_context=extra_context)
    
    actions = ['activate_selected', 'deactivate_selected', 'export_as_csv']
    
    def activate_selected(self, request, queryset):
        """Bulk activate subscriptions."""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f'{updated} subscription(s) were successfully activated.'
        )
    activate_selected.short_description = "Activate selected subscriptions"
    
    def deactivate_selected(self, request, queryset):
        """Bulk deactivate subscriptions."""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f'{updated} subscription(s) were successfully deactivated.'
        )
    deactivate_selected.short_description = "Deactivate selected subscriptions"
    
    def export_as_csv(self, request, queryset):
        """Export subscriptions as CSV."""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="newsletter_subscriptions.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Email', 'Active', 'Subscribed At', 'IP Address'])
        
        for subscription in queryset:
            writer.writerow([
                subscription.email,
                'Yes' if subscription.is_active else 'No',
                subscription.subscribed_at.strftime('%Y-%m-%d %H:%M:%S'),
                subscription.ip_address or 'N/A',
            ])
        
        return response
    export_as_csv.short_description = "Export selected as CSV"


# Customize the admin site header
admin.site.site_header = "Wax and Warmth Admin"
admin.site.site_title = "Wax and Warmth Admin Portal"
admin.site.index_title = "Welcome to Wax and Warmth Administration"