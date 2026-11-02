# Wax and Warmth

React + Vite storefront and Django REST Framework API.

## Local development

1. Copy `.env.example` to the project root as `.env`. Keep production secrets out of Git.
2. In `backend/`, create and activate a virtual environment, then install dependencies:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

   Development uses `backend/dev.sqlite3`. The old database files are preserved under `backups/` and are not used by the app. Set `DJANGO_SETTINGS_MODULE=config.settings.production`, database credentials, and a shared Redis `REDIS_URL` for a production deployment. Redis backs the cross-worker authentication throttles.
3. In `frontend/`, install packages and create `frontend/.env.local` containing only the public API URL:

   ```text
   VITE_API_URL=http://localhost:8000/api
   ```

   Then run `npm install` and `npm run dev`.

### Load the original product catalog

After starting the backend and applying migrations, import the checked-in catalog once:

```powershell
cd backend
python manage.py seed_catalog
```

The importer is safe to rerun and adds the 16 products whose images are bundled under `frontend/public/wax`. Products start with zero stock; add quantities from the admin inventory panel before enabling purchases. Uploaded images are served from the backend media directory during development.

## Authentication and security

- Registration validates passwords with Django's configured password validators, then hashes them through Django's user manager. Public registration cannot assign the admin role.
- Login and registration return a short-lived access token. The rotating refresh token is stored in an HttpOnly cookie scoped to `/api/auth/`; JavaScript cannot read it. The frontend keeps the access token in memory and restores sessions through the cookie.
- Logout blacklists the refresh token and clears its cookie. Login and registration are rate limited; password and profile inputs are validated server side. Admin actions use backend role permissions, regardless of frontend route guards.
- Production settings reject the example secret, localhost-only hosts, and non-HTTPS CORS origins. Use HTTPS, a unique `SECRET_KEY`, production database credentials, and the exact frontend origin in `CORS_ALLOWED_ORIGINS`.
- For a frontend and API on separate sites, set `JWT_COOKIE_SAMESITE=None` and `JWT_COOKIE_SECURE=True`; configure the frontend origin in `CORS_ALLOWED_ORIGINS`. Keep the root `.env` server-side. Never place database passwords, Django keys, or other secrets in `frontend/.env*` or any `VITE_*` variable.

See `backend/DATABASE_SCHEMA.md` for the data model and the API documentation in `backend/README.md`.

## Project layout

- `frontend/` — React storefront, static product images, and browser routing.
- `backend/` — Django REST API, migrations, and admin.
- `backups/` — local-only SQLite archives from the pre-consolidation folders; excluded from Git.
- `render.yaml` and `DEPLOY_FREE.md` — backend deployment blueprint and setup guide.
