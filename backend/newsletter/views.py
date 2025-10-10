from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.template import RequestContext
import json
import logging
import os

from .models import NewsletterSubscription


logger = logging.getLogger(__name__)


def serve_html_file(request, filename):
    """Serve HTML files with Django template processing."""
    from django.template.loader import get_template
    from django.template import Template, Context
    from django.http import HttpResponse
    import os
    
    # Define the path to the HTML files (parent directory of backend)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    html_file_path = os.path.join(base_dir, filename)
    
    # Check if file exists
    if not os.path.exists(html_file_path):
        # Try alternative path
        alt_path = os.path.join(os.path.dirname(base_dir), filename)
        if os.path.exists(alt_path):
            html_file_path = alt_path
        else:
            return JsonResponse({
                'error': 'File not found', 
                'tried_paths': [html_file_path, alt_path]
            }, status=404)
    
    # Read the HTML file
    with open(html_file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    # Create a template from the HTML content
    template = Template(html_content)
    
    # Create context with request and CSRF token
    from django.template.context_processors import csrf
    context = Context({
        'request': request,
        'csrf_token': csrf(request)['csrf_token'],
    })
    
    # Render the template
    rendered_html = template.render(context)
    
    return HttpResponse(rendered_html, content_type='text/html')


def home_view(request):
    """Serve the index.html file."""
    return serve_html_file(request, 'index.html')


def get_client_ip(request):
    """Get the client's IP address from the request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@require_http_methods(["GET", "POST"])
def newsletter_subscribe(request):
    """Handle newsletter subscription requests."""
    
    if request.method == 'GET':
        # Return the subscription page or redirect to home
        return redirect('/')
    
    # Handle POST request
    try:
        # Get email from form data
        email = request.POST.get('email', '').strip().lower()
        
        if not email:
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({
                    'success': False,
                    'message': 'Email address is required.'
                }, status=400)
            else:
                messages.error(request, 'Email address is required.')
                return redirect('/')
        
        # Validate email format
        if '@' not in email or '.' not in email:
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({
                    'success': False,
                    'message': 'Please enter a valid email address.'
                }, status=400)
            else:
                messages.error(request, 'Please enter a valid email address.')
                return redirect('/')
        
        # Get additional data
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Try to create the subscription
        try:
            subscription = NewsletterSubscription.objects.create(
                email=email,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Store email in session for display purposes
            request.session['newsletter_email'] = email
            
            logger.info(f"New newsletter subscription: {email}")
            
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({
                    'success': True,
                    'message': 'Successfully subscribed to our newsletter!'
                })
            else:
                messages.success(request, 'Successfully subscribed to our newsletter!')
                return redirect('/')
                
        except IntegrityError:
            # Email already exists
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({
                    'success': False,
                    'message': 'This email is already subscribed to our newsletter.'
                }, status=400)
            else:
                messages.warning(request, 'This email is already subscribed to our newsletter.')
                return redirect('/')
                
    except Exception as e:
        logger.error(f"Newsletter subscription error: {str(e)}")
        
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({
                'success': False,
                'message': 'An error occurred. Please try again later.'
            }, status=500)
        else:
            messages.error(request, 'An error occurred. Please try again later.')
            return redirect('/')


@csrf_exempt
@require_POST
def newsletter_subscribe_api(request):
    """API endpoint for newsletter subscription (JSON)."""
    
    try:
        # Parse JSON data
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        
        if not email:
            return JsonResponse({
                'success': False,
                'message': 'Email address is required.'
            }, status=400)
        
        # Validate email format
        if '@' not in email or '.' not in email:
            return JsonResponse({
                'success': False,
                'message': 'Please enter a valid email address.'
            }, status=400)
        
        # Get additional data
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Try to create the subscription
        try:
            subscription = NewsletterSubscription.objects.create(
                email=email,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            logger.info(f"New newsletter subscription via API: {email}")
            
            return JsonResponse({
                'success': True,
                'message': 'Successfully subscribed to our newsletter!',
                'subscription_id': subscription.id
            })
            
        except IntegrityError:
            return JsonResponse({
                'success': False,
                'message': 'This email is already subscribed to our newsletter.'
            }, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data.'
        }, status=400)
        
    except Exception as e:
        logger.error(f"Newsletter API subscription error: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'An error occurred. Please try again later.'
        }, status=500)


def newsletter_unsubscribe(request):
    """Handle newsletter unsubscription."""
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        
        if email:
            try:
                subscription = NewsletterSubscription.objects.get(email=email)
                subscription.deactivate()
                
                messages.success(request, 'Successfully unsubscribed from our newsletter.')
                logger.info(f"Newsletter unsubscription: {email}")
                
            except NewsletterSubscription.DoesNotExist:
                messages.warning(request, 'Email address not found in our subscription list.')
                
        else:
            messages.error(request, 'Email address is required.')
    
    return redirect('/')


def newsletter_stats(request):
    """Simple stats view for newsletter subscriptions (admin use)."""
    
    if not request.user.is_staff:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    total_subscriptions = NewsletterSubscription.objects.count()
    active_subscriptions = NewsletterSubscription.objects.filter(is_active=True).count()
    inactive_subscriptions = NewsletterSubscription.objects.filter(is_active=False).count()
    
    return JsonResponse({
        'total_subscriptions': total_subscriptions,
        'active_subscriptions': active_subscriptions,
        'inactive_subscriptions': inactive_subscriptions
    })