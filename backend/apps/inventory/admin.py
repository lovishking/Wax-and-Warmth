from django.contrib import admin
from .models import Inventory, InventoryTransaction


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity', 'reserved_quantity', 'reorder_level', 'updated_at']
    list_filter = ['reorder_level']
    search_fields = ['product__name']
    readonly_fields = ['product', 'quantity', 'reserved_quantity', 'reorder_level', 'updated_at']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ['product', 'transaction_type', 'quantity', 'previous_quantity', 'new_quantity', 'created_at']
    list_filter = ['transaction_type']
    search_fields = ['product__name', 'reason']
    readonly_fields = [
        'product', 'transaction_type', 'quantity', 'previous_quantity', 'new_quantity',
        'previous_reserved', 'new_reserved', 'reason', 'reference_id', 'created_by', 'created_at',
    ]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
