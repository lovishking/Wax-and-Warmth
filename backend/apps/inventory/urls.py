"""
Inventory URL Configuration
"""

from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.InventoryListView.as_view(), name='list'),
    path('<int:pk>/', views.InventoryDetailView.as_view(), name='detail'),
    path('restock/', views.RestockView.as_view(), name='restock'),
    path('adjust/', views.AdjustStockView.as_view(), name='adjust'),
    path('reorder-level/', views.SetReorderLevelView.as_view(), name='reorder-level'),
    path('low-stock/', views.LowStockView.as_view(), name='low-stock'),
    path('out-of-stock/', views.OutOfStockView.as_view(), name='out-of-stock'),
    path('transactions/', views.InventoryTransactionListView.as_view(), name='transactions'),
    path('dashboard/', views.DashboardStatsView.as_view(), name='dashboard'),
]
