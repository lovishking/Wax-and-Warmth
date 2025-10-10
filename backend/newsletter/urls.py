from django.urls import path
from . import views

app_name = 'newsletter'

urlpatterns = [
    # HTML page serving
    path('', views.home_view, name='home'),
    path('about/', lambda request: views.serve_html_file(request, 'about.html'), name='about'),
    path('shop/', lambda request: views.serve_html_file(request, 'shop.html'), name='shop'),
    path('blog/', lambda request: views.serve_html_file(request, 'blog.html'), name='blog'),
    path('contact/', lambda request: views.serve_html_file(request, 'contact.html'), name='contact'),
    path('cart/', lambda request: views.serve_html_file(request, 'cart.html'), name='cart'),
    path('sproduct/', lambda request: views.serve_html_file(request, 'sproduct.html'), name='sproduct'),
    
    # Newsletter subscription endpoints
    path('newsletter-signup/', views.newsletter_subscribe, name='subscribe'),
    path('newsletter-login/', views.newsletter_subscribe, name='subscribe_alt'),  # Alternative URL for form action
    path('api/newsletter/subscribe/', views.newsletter_subscribe_api, name='subscribe_api'),
    
    # Newsletter unsubscription
    path('newsletter-unsubscribe/', views.newsletter_unsubscribe, name='unsubscribe'),
    
    # Stats endpoint (admin only)
    path('newsletter-stats/', views.newsletter_stats, name='stats'),
]