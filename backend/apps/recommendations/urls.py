"""
Recommendations URL Configuration
"""

from django.urls import path
from . import views

app_name = 'recommendations'

urlpatterns = [
    path('update/', views.UpdateKnowledgeView.as_view(), name='update-knowledge'),
    path('update/<int:product_id>/', views.UpdateProductKnowledgeView.as_view(), name='update-product-knowledge'),
]
