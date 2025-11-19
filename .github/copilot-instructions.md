# Wax and Warmth - AI Coding Agent Instructions

## Project Architecture

**Wax and Warmth** is a hybrid e-commerce platform with a **Django backend** and **vanilla HTML/CSS/JavaScript frontend**, deployed to Vercel.

### Key Components

- **Frontend** (`*.html`, `script.js`, `admin-dashboard.js`): Client-side e-commerce UI with shopping cart, product catalog, and admin dashboard
- **Backend** (`backend/`): Django 5.0+ REST API for newsletter subscriptions, product management, and admin authentication
- **Data Storage**: Browser localStorage (frontend products) + SQLite (newsletter subscriptions)
- **Deployment**: Vercel (static + Django backend via serverless functions)

## Frontend Architecture Patterns

### LocalStorage-First Data Model

- **Products**: Stored as JSON in localStorage (`localStorage.getItem("products")`), synced across all pages
- **Cart**: Stored as `cart` key with structure: `[{name, price, image, quantity}, ...]`
- **Admin Session**: Tracked via `adminSession`, `adminUsername`, `sessionToken`, `loginTimestamp`
- **Key Pattern**: Always use `JSON.parse()` with fallback to empty array: `JSON.parse(localStorage.getItem("key")) || []`

### Adding/Modifying Frontend Features

1. Cart operations in `script.js`: `addToCart()`, `updateQuantity()`, `removeItem()`
2. Admin dashboard sections: use `showSection()` to toggle `.content-section` visibility
3. Products display dynamically when localStorage updates—no page refresh needed
4. Mobile detection pattern: check `navigator.userAgent` for mobile UX adjustments

### Security Note: Admin Panel

- `admin-security.js`: Blocks console access, detects dev tools, sanitizes console output
- Authentication: Credentials validated client-side using encrypted session tokens
- Session expiry: 24-hour timeout via `loginTimestamp`
- When modifying admin logic, preserve session validation in `checkAuth()`

## Backend Architecture

### Django Newsletter App (`backend/newsletter/`)

- **Models** (`models.py`): `NewsletterSubscription` with email uniqueness constraint, active status, IP/user-agent tracking
- **Views** (`views.py`): Handles `/newsletter-login/`, `/api/newsletter/subscribe/`, `/newsletter-unsubscribe/`
- **CORS Enabled**: `django-cors-headers` middleware active for cross-origin requests
- **CSRF Protection**: Django CSRF tokens required for form submissions, embedded in HTML templates

### Critical Django Settings

- `DEBUG = False` in production (Vercel deployment)
- `ALLOWED_HOSTS`: `['wax-and-warmth.shop', 'www.wax-and-warmth.shop', 'localhost', '.vercel.app']`
- `SECRET_KEY`: Set via `DJANGO_SECRET_KEY` environment variable—must be configured for deployment
- SQLite database: `backend/db.sqlite3`

### Newsletter API Endpoints

- **POST** `/newsletter-login/`: Form submission (returns redirect or message)
- **POST** `/api/newsletter/subscribe/`: JSON API (returns `{success: bool, message: str}`)
- **POST** `/newsletter-unsubscribe/`: Email-based unsubscribe
- **GET** `/newsletter-stats/`: Admin statistics (authentication required)

### Adding Backend Features

1. Run migrations: `python manage.py makemigrations` → `python manage.py migrate`
2. Update `settings.py` for new apps (add to `INSTALLED_APPS`)
3. Test locally: `python manage.py runserver` (port 8000)
4. Use `test_backend.py` for verification after changes

## Critical Developer Workflows

### Local Development Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Frontend: Open any `.html` file directly in browser (or use live server)

### Deployment to Vercel

- `deploy.sh`: Auto-runs migrations and collects static files
- `vercel.json`: Configures URL rewrites for all pages (e.g., `/shop` → `/shop.html`)
- Environment variables required: `DJANGO_SECRET_KEY`, `DEBUG=False`
- Frontend deploys automatically; Django backend runs via serverless functions

### Testing

- Backend: Run `python test_backend.py` after server starts
- Frontend: Check browser console for localStorage errors, verify cart persistence across pages
- Admin login: Navigate to `/admin-login.html`, uses encrypted credential validation

## Project-Specific Conventions

### Naming & Patterns

- Page files: lowercase with hyphens (e.g., `product-images.js`, `admin-login.html`)
- JavaScript functions: camelCase, prefixed by concern (e.g., `displayCartTable()`, `loadProducts()`)
- Django URLs: kebab-case with trailing slash convention (e.g., `/newsletter-login/`, `/api/newsletter/subscribe/`)
- CSS classes: kebab-case, grid-based layout (Flexbox/CSS Grid used throughout)

### Image & Asset Handling

- Product images: Stored as base64 in localStorage via `admin-dashboard.js`
- Recommended size: 500x500px for performance
- Supported formats: JPG, PNG, GIF, WebP
- Image directories: `/images/`, `/products/`, `/vids/`

### Form Handling

- Newsletter forms post to `/newsletter-login/` with CSRF token
- Admin forms in `admin-dashboard.js`: use localStorage directly for product CRUD
- Mobile forms: Use native form elements for better UX on touch devices

## Integration Points & Dependencies

### External Services & Middleware

- **django-cors-headers**: Required for frontend-to-backend communication across different origins
- **Pillow**: Image processing in Django
- **python-decouple**: Environment variable management (used for `DJANGO_SECRET_KEY`)

### Frontend-Backend Communication

- Forms submit to Django via POST to `/newsletter-login/`
- Admin dashboard: Reads/writes products to localStorage (no backend sync currently)
- Newsletter subscriptions: Form → Django validation → SQLite storage

### Vercel Integration

- Static files (HTML, CSS, JS) served from root
- Django backend: Rewrite rules configured in `vercel.json` to route requests appropriately
- **Important**: All `.html` pages are rewritten automatically; no file extensions needed in URLs

## Common Modification Patterns

### Adding a New Page

1. Create `newpage.html` in project root
2. Add rewrite rule to `vercel.json`: `{"source": "/newpage", "destination": "/newpage.html"}`
3. Link from navbar in `index.html` or other pages
4. Import `script.js` for shared utilities

### Adding Products Programmatically

Frontend: `JSON.stringify({name, price, image, category, stock})` → localStorage
Backend: Add model field to `NewsletterSubscription` or create new Django model

### Modifying Admin Dashboard

1. Edit `admin-dashboard.js` for functionality
2. Update `admin-dashboard.html` for UI
3. Preserve session checks in `checkAuth()` to maintain security
4. Test with dev tools detector disabled locally via browser console

## Troubleshooting Patterns

- **Products not showing**: Check localStorage in dev tools; verify `loadProducts()` called on page load
- **Newsletter signup failing**: Check `DJANGO_SECRET_KEY` set, CORS middleware active, `/newsletter-login/` endpoint responding
- **Admin login issues**: Clear browser storage, verify session token generated in `admin-login.html`
- **Deployment fails**: Run `deploy.sh` locally first, verify migrations execute without errors

---

**Last Updated**: November 20, 2025  
**Framework Versions**: Django 5.0+, Python 3.8+, Vanilla JS ES6+
