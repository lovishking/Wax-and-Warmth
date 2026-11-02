"""
Order URL Configuration
"""

from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.MyOrdersView.as_view(), name='my-orders'),
    path('create/', views.CreateOrderView.as_view(), name='create'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='detail'),
    path('<int:pk>/cancel/', views.CancelOrderView.as_view(), name='cancel'),
    # Admin
    path('admin/sales/', views.AdminSalesView.as_view(), name='admin-sales'),
    path('admin/', views.AdminOrderListView.as_view(), name='admin-list'),
    path('admin/<int:pk>/status/', views.AdminUpdateOrderStatusView.as_view(), name='admin-update-status'),
]
