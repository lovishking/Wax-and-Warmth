from django.contrib import admin
from .models import Product, ProductFacet, ProductFacetAssignment, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'scent_family', 'is_active', 'is_featured']
    list_filter = ['category', 'scent_family', 'fragrance_strength', 'size', 'is_active']
    search_fields = ['name', 'description', 'facet_assignments__facet__value']
    prepopulated_fields = {'slug': ('name',)}
    inlines = []

    def has_delete_permission(self, request, obj=None):
        return False


class ProductFacetInline(admin.TabularInline):
    model = ProductFacetAssignment
    extra = 0
    autocomplete_fields = ['facet']


ProductAdmin.inlines = [ProductFacetInline]


@admin.register(ProductFacet)
class ProductFacetAdmin(admin.ModelAdmin):
    list_display = ['value', 'kind', 'normalized_value']
    list_filter = ['kind']
    search_fields = ['value', 'normalized_value']
    readonly_fields = ['normalized_value']
