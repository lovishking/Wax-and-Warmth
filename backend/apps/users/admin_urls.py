from django.urls import path

from .views import AdminUserListView, AdminUserStatusView

app_name = 'admin_users'

urlpatterns = [
    path('', AdminUserListView.as_view(), name='list'),
    path('<int:pk>/', AdminUserStatusView.as_view(), name='status'),
]
