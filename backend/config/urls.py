"""
Wax & Warmth URL Configuration
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.http import Http404, JsonResponse
from django.views.static import serve
from django.utils import timezone
from pathlib import Path


def health_check(request):
    """Lightweight health check endpoint for uptime monitors and keep-alive pings."""
    return JsonResponse({
        'status': 'ok',
        'service': 'wax-and-warmth-backend',
        'timestamp': timezone.now().isoformat(),
    })


def serve_development_media(request, path):
    if not settings.DEBUG:
        raise Http404('Development media serving is disabled.')
    media_root = Path(settings.MEDIA_ROOT)
    uploaded_file = media_root / path
    if uploaded_file.is_file():
        return serve(request, path, document_root=media_root)

    # The checked-in catalog images ship with the frontend. Uploaded files stay
    # in MEDIA_ROOT and take precedence above.
    if path.startswith(('products/', 'categories/')):
        bundled_assets = Path(settings.BASE_DIR).parent / 'frontend' / 'public' / 'wax'
        bundled_file = bundled_assets / path
        if bundled_file.is_file():
            return serve(request, path, document_root=bundled_assets)
    raise Http404('Media file not found.')

urlpatterns = [
    path('api/health/', health_check, name='health_check'),
    path('healthz/', health_check, name='healthz'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.urls')),
    path('api/users/', include('apps.users.admin_urls')),
    path('api/products/', include('apps.products.urls')),
    path('api/inventory/', include('apps.inventory.urls')),
    path('api/cart/', include('apps.cart.urls')),
    path('api/orders/', include('apps.orders.urls')),
    path('api/chat/', include('apps.chatbot.urls')),
    path('api/recommendations/', include('apps.recommendations.urls')),
    path('api/newsletter/', include('apps.newsletter.urls')),
    path('api/settings/', include('apps.storefront.urls')),
]

urlpatterns += [re_path(r'^media/(?P<path>.*)$', serve_development_media)]
