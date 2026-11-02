from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'product_name', 'quantity', 'unit_price', 'subtotal']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_amount', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['user__email', 'id']
    inlines = [OrderItemInline]
    readonly_fields = ['user', 'total_amount', 'created_at', 'updated_at']

    def has_delete_permission(self, request, obj=None):
        return False
