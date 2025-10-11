"""
URL configuration for wax_and_warmth project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf.
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.http import HttpResponse, Http404
import os
import mimetypes

def serve_static_with_headers(request, path):
    """Serve static files with proper headers."""
    parent_dir = os.path.dirname(settings.BASE_DIR)
    file_path = os.path.join(parent_dir, path)
    
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise Http404("File not found")
    
    # Get MIME type
    content_type, _ = mimetypes.guess_type(file_path)
    if not content_type:
        content_type = 'application/octet-stream'
    
    # Read file content
    with open(file_path, 'rb') as f:
        content = f.read()
    
    # Create response with proper headers
    response = HttpResponse(content, content_type=content_type)
    response['Access-Control-Allow-Origin'] = '*'
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    
    return response

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('newsletter.urls')),  # Include newsletter URLs at root level
]

# Serve static files during development
if settings.DEBUG:
    import re
    from django.urls import re_path
    
    urlpatterns += [
        re_path(r'^(?P<path>.*\.(css|js|jpg|jpeg|png|gif|ico|svg|woff|woff2|ttf|eot))$', 
                serve_static_with_headers),
        re_path(r'^images/(?P<path>.*)$', 
                lambda request, path: serve_static_with_headers(request, f'images/{path}')),
        re_path(r'^products/(?P<path>.*)$', 
                lambda request, path: serve_static_with_headers(request, f'products/{path}')),
        re_path(r'^testi/(?P<path>.*)$', 
                lambda request, path: serve_static_with_headers(request, f'testi/{path}')),
        re_path(r'^vids/(?P<path>.*)$', 
                lambda request, path: serve_static_with_headers(request, f'vids/{path}')),
    ]