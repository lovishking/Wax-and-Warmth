"""
Wax & Warmth - Production Settings
Uses PostgreSQL and tighter security.
"""

from .base import *  # noqa: F401, F403
from django.core.exceptions import ImproperlyConfigured

DEBUG = False

if not SECRET_KEY or SECRET_KEY in {
    'your-secret-key-here', 'replace-with-a-unique-random-secret',
    'django-insecure-local-development-only',
}:
    raise ImproperlyConfigured('Set a unique SECRET_KEY before using production settings.')
if ALLOWED_HOSTS == ['localhost', '127.0.0.1']:
    raise ImproperlyConfigured('Set ALLOWED_HOSTS to the deployed API host in production.')
if not CORS_ALLOWED_ORIGINS or any(origin.startswith('http://') for origin in CORS_ALLOWED_ORIGINS):
    raise ImproperlyConfigured('Set CORS_ALLOWED_ORIGINS to the HTTPS frontend origin(s) in production.')
if not JWT_COOKIE_SECURE:
    raise ImproperlyConfigured('JWT_COOKIE_SECURE must be true in production.')
if REDIS_URL in {'redis://localhost:6379/0', 'redis://127.0.0.1:6379/0'}:
    raise ImproperlyConfigured('Set REDIS_URL to the shared production Redis service.')

# PostgreSQL for production. DATABASE_URL is convenient for managed providers;
# individual DB_* variables remain supported for local and container deployments.
database_url = env('DATABASE_URL', default='')
if database_url:
    DATABASES = {'default': env.db_url_config(database_url)}
    DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql'
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env('DB_NAME', default='wax_and_warmth'),
            'USER': env('DB_USER', default='wax_user'),
            'PASSWORD': env('DB_PASSWORD'),
            'HOST': env('DB_HOST', default='localhost'),
            'PORT': env('DB_PORT', default='5432'),
        }
    }
DATABASES['default']['CONN_MAX_AGE'] = env.int('DB_CONN_MAX_AGE', default=60)

# Shared cache keeps authentication throttles effective across workers.
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'},
        'KEY_PREFIX': 'wax-and-warmth',
    },
}

# Security
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=True)
SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS', default=31536000)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True)
SECURE_HSTS_PRELOAD = env.bool('SECURE_HSTS_PRELOAD', default=False)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])
