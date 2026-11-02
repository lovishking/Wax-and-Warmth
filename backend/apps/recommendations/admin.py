from django.contrib import admin
from .models import CandleKnowledge


@admin.register(CandleKnowledge)
class CandleKnowledgeAdmin(admin.ModelAdmin):
    list_display = ['product', 'embedding_model', 'updated_at']
    search_fields = ['product__name']
    readonly_fields = ['embedding']
