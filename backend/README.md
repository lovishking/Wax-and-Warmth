# Wax and Warmth - Django Backend Setup

This Django backend handles newsletter email subscriptions for the Wax and Warmth website.

## Features

- **Newsletter Subscription Management**: Store and manage email subscriptions
- **Django Admin Interface**: Easy-to-use admin panel for managing subscriptions
- **API Endpoints**: RESTful API for newsletter subscriptions
- **CORS Support**: Cross-origin resource sharing for frontend integration
- **Email Validation**: Proper email validation and duplicate prevention
- **Session Management**: Track subscribed users

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Navigate to Backend Directory

```bash
cd backend
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Database Setup

```bash
# Create database migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### Step 5: Create Admin User (Optional)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin user for accessing the Django admin panel.

### Step 6: Run Development Server

```bash
python manage.py runserver
```

The Django backend will be available at: `http://127.0.0.1:8000/`

## API Endpoints

### Newsletter Subscription

- **POST** `/newsletter-login/` - Subscribe to newsletter (form submission)
- **POST** `/api/newsletter/subscribe/` - Subscribe to newsletter (JSON API)
- **POST** `/newsletter-unsubscribe/` - Unsubscribe from newsletter
- **GET** `/newsletter-stats/` - Get subscription statistics (admin only)

### Admin Panel

- **URL**: `http://127.0.0.1:8000/admin/`
- **Features**:
  - View all newsletter subscriptions
  - Activate/deactivate subscriptions
  - Export subscriptions as CSV
  - Search and filter subscriptions
  - Bulk actions

## Frontend Integration

The HTML forms in your frontend files have been updated to work with this Django backend:

1. **Form Action**: All newsletter forms now submit to `/newsletter-login/`
2. **CSRF Protection**: Django CSRF tokens are included in forms
3. **Success Messages**: Users see confirmation messages after subscribing
4. **Session Tracking**: Subscribed emails are stored in session for display

## File Structure

```
backend/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── wax_and_warmth/          # Main Django project
│   ├── __init__.py
│   ├── settings.py          # Django settings
│   ├── urls.py              # Main URL configuration
│   ├── wsgi.py              # WSGI configuration
│   └── asgi.py              # ASGI configuration
└── newsletter/              # Newsletter Django app
    ├── __init__.py
    ├── admin.py             # Admin interface configuration
    ├── apps.py              # App configuration
    ├── models.py            # Database models
    ├── urls.py              # App URL configuration
    └── views.py             # View functions
```

## Database Schema

### NewsletterSubscription Model

| Field         | Type                  | Description                 |
| ------------- | --------------------- | --------------------------- |
| email         | EmailField            | Subscriber's email (unique) |
| subscribed_at | DateTimeField         | Subscription timestamp      |
| is_active     | BooleanField          | Subscription status         |
| ip_address    | GenericIPAddressField | Subscriber's IP address     |
| user_agent    | TextField             | Browser information         |

## Security Considerations

1. **CSRF Protection**: Enabled for all forms
2. **Email Validation**: Server-side email validation
3. **Duplicate Prevention**: Unique email constraint
4. **IP Logging**: Track subscription sources
5. **Admin Authentication**: Secure admin access

## Production Deployment

For production deployment, update the following in `settings.py`:

1. Set `DEBUG = False`
2. Configure `ALLOWED_HOSTS`
3. Use environment variables for secret keys
4. Configure proper database (PostgreSQL recommended)
5. Set up email backend for notifications
6. Configure static file serving

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're in the correct directory and virtual environment is activated
2. **Database Issues**: Run migrations with `python manage.py migrate`
3. **CSRF Errors**: Ensure CSRF tokens are included in forms
4. **CORS Issues**: Check CORS settings in `settings.py`

### Logs

Django logs are displayed in the console when running the development server. Check for any error messages there.

## Support

For issues or questions, please check:

1. Django official documentation: https://docs.djangoproject.com/
2. Django CORS headers documentation: https://github.com/adamchainz/django-cors-headers
3. Project repository for updates and issues
