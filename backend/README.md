# Django REST Framework backend

## Run locally

Use Python 3.11+ and install `requirements.txt` in a virtual environment. Copy the root `.env.example` to the repository root as `.env`, then run:

```powershell
cd backend
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Development uses `backend/dev.sqlite3`. Pre-consolidation databases are archived under `backups/` and are not connected to the app. Production uses PostgreSQL when `DJANGO_SETTINGS_MODULE=config.settings.production` is selected; configure `DATABASE_URL` or the `DB_*` variables, a shared Redis `REDIS_URL`, a unique `SECRET_KEY`, `ALLOWED_HOSTS`, HTTPS frontend `CORS_ALLOWED_ORIGINS`, and `DEBUG=False` in the deployment environment.

## Authentication security

- `POST /api/auth/register/` creates customer accounts only and validates passwords with Django's password validators.
- `POST /api/auth/login/` returns an access token and sets a rotating refresh token in an HttpOnly, path-scoped cookie. Refresh tokens are never returned to frontend JavaScript.
- `POST /api/auth/token/refresh/` rotates the cookie and returns a new access token. `POST /api/auth/logout/` blacklists the refresh token and clears the cookie.
- Login, registration, and refresh use scoped rate limits. Stateful auth endpoints validate browser origins against `CORS_ALLOWED_ORIGINS`.
- Authenticated profile, order, cart, and admin API views enforce permissions on the server. Client route guards only control navigation and are not authorization checks.

For local HTTP development, `JWT_COOKIE_SECURE=False` is set in the example environment. Production must use HTTPS and `JWT_COOKIE_SECURE=True`. If the frontend and API are on different sites, use `JWT_COOKIE_SAMESITE=None` with secure cookies and credentialed CORS for the exact frontend origin. See the root `README.md` for setup and the root `.env.example` for variable names.
