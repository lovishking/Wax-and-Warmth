from django.urls import path

from .views import (
    AdminClearSubscriptionsView,
    AdminNewsletterStatsView,
    AdminSubscriptionDetailView,
    AdminSubscriptionListView,
    SubscribeView,
    UnsubscribeView,
)

app_name = 'newsletter'

urlpatterns = [
    path('subscribe/', SubscribeView.as_view(), name='subscribe'),
    path('unsubscribe/', UnsubscribeView.as_view(), name='unsubscribe'),
    path('admin/', AdminSubscriptionListView.as_view(), name='admin-list'),
    path('admin/clear/', AdminClearSubscriptionsView.as_view(), name='admin-clear'),
    path('admin/<int:pk>/', AdminSubscriptionDetailView.as_view(), name='admin-detail'),
    path('admin/stats/', AdminNewsletterStatsView.as_view(), name='admin-stats'),
]
