from django.urls import path

from .views import SiteSettingsView

app_name = 'storefront'

urlpatterns = [path('', SiteSettingsView.as_view(), name='settings')]
