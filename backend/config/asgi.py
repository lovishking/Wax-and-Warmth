"""
ASGI config for Wax & Warmth project.
"""

import os
from pathlib import Path

import environ
from django.core.asgi import get_asgi_application

env_file = Path(__file__).resolve().parents[2] / '.env'
if env_file.exists():
    environ.Env.read_env(str(env_file))

os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    os.environ.get('DJANGO_SETTINGS_MODULE', 'config.settings.development'),
)
application = get_asgi_application()
