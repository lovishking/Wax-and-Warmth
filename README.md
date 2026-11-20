# Wax & Warmth

A full-stack e-commerce platform for discovering and purchasing handcrafted candles. Wax & Warmth combines a customer-facing storefront with a Django REST API and an admin workflow for managing products, inventory, and orders.

**Live application:** https://wax-and-warmth.jaiswal-lovish-official.workers.dev/  
**Repository:** https://github.com/lovishking/Wax-and-Warmth

## Overview

Wax & Warmth is built to support the complete candle-shopping experience, from browsing products to managing orders and store inventory. The application uses a React frontend and a Django REST Framework backend, with PostgreSQL for production data storage.

## Features

### Storefront
- Browse the candle catalogue and view product information.
- Add products to a shopping cart and manage cart items.
- Register and log in to a customer account.
- View customer profile and order information.
- Get candle discovery assistance through the recommendation/chatbot functionality.

### Administration and inventory
- Manage products and catalogue information.
- Maintain inventory and stock availability.
- Review and manage customer orders.
- Keep stock validation on the server side to help prevent invalid purchases.

### Backend and security
- REST APIs built with Django REST Framework.
- JWT-based authentication with short-lived access tokens and rotating refresh tokens stored in HttpOnly cookies.
- Server-side permission checks for customer and administrative operations.
- PostgreSQL support for production and SQLite for local development.
- Redis integration and Celery support for background processing.
- CORS, CSRF, and configurable environment-based settings.

## Tech Stack

| Layer | Technologies |
|---|---|
| Frontend | React 19, Vite, React Router, Axios, Lucide React |
| Backend | Python, Django, Django REST Framework |
| Database | SQLite (development), PostgreSQL (production), pgvector |
| Authentication | Simple JWT, HttpOnly refresh-token cookies |
| Background services | Redis, Celery |
| AI / recommendations | OpenAI API, Sentence Transformers, NumPy |
| Deployment server | Gunicorn |

## Project Structure

```text
Wax-and-Warmth/
├── backend/
│   ├── apps/
│   │   ├── cart/
│   │   ├── chatbot/
│   │   ├── inventory/
│   │   ├── newsletter/
│   │   ├── orders/
│   │   ├── products/
│   │   ├── recommendations/
│   │   ├── storefront/
│   │   └── users/
│   ├── config/
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── api/
│   │   ├── auth/
│   │   ├── components/
│   │   ├── context/
│   │   └── pages/
│   ├── package.json
│   └── vite.config.js
├── backups/
├── .env.example
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.11 or later
- Node.js and npm
- Git
- PostgreSQL and Redis for production-like/local service configurations (the default development database is SQLite)

### 1. Clone the repository

```bash
git clone https://github.com/lovishking/Wax-and-Warmth.git
cd Wax-and-Warmth
```

### 2. Configure environment variables

Copy the example environment file in the repository root:

**Windows PowerShell**
```powershell
Copy-Item .env.example .env
```

**macOS / Linux**
```bash
cp .env.example .env
```

Update the values in `.env` as required. At minimum, set a unique Django `SECRET_KEY`. For local development, the example configuration uses SQLite and local frontend/API origins. Add your OpenAI API key if you want to use the AI-powered recommendation/chatbot features.

Do not commit your real `.env` file or production secrets.

### 3. Set up the backend

Create and activate a virtual environment from the repository root:

**Windows PowerShell**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies and start Django:

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The backend API is available at:

```text
http://127.0.0.1:8000/
```

The Django admin panel is available at:

```text
http://127.0.0.1:8000/admin/
```

### 4. Set up the frontend

Open a second terminal from the repository root:

```bash
cd frontend
npm install
npm run dev
```

Vite starts the frontend (normally at `http://localhost:5173`). The frontend API base URL is configured through `VITE_API_URL` in the root `.env` file; the example value is `http://localhost:8000/api`.

### 5. Build the frontend

To create a production frontend build:

```bash
cd frontend
npm run build
```

To preview the generated build locally:

```bash
npm run preview
```

## Environment Configuration

The root [`.env.example`](.env.example) documents the supported environment variables, including:

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | Enables/disables Django debug mode |
| `DJANGO_SETTINGS_MODULE` | Selects development or production settings |
| `DATABASE_URL` / `DB_*` | Database connection |
| `REDIS_URL` | Redis connection |
| `JWT_ACCESS_TOKEN_LIFETIME` | Access-token lifetime in minutes |
| `JWT_REFRESH_TOKEN_LIFETIME` | Refresh-token lifetime in minutes |
| `OPENAI_API_KEY` | API key for AI functionality |
| `CORS_ALLOWED_ORIGINS` | Allowed frontend origins |
| `VITE_API_URL` | API base URL used by the frontend |

For production, use PostgreSQL, set `DEBUG=False`, configure `ALLOWED_HOSTS`, use a strong unique `SECRET_KEY`, and serve the application over HTTPS. Set `JWT_COOKIE_SECURE=True` in production. Configure CORS and CSRF trusted origins for the exact deployed frontend domain.

## API and Authentication Notes

The backend exposes its API under the `/api/` prefix. Authentication endpoints include:

- `POST /api/auth/register/` — create a customer account.
- `POST /api/auth/login/` — authenticate and receive an access token; the refresh token is set in an HttpOnly cookie.
- `POST /api/auth/token/refresh/` — rotate the refresh cookie and obtain a new access token.
- `POST /api/auth/logout/` — invalidate the refresh token and clear the cookie.

Authenticated customer and administrative endpoints enforce permissions on the server. Frontend route guards are for navigation only and are not a substitute for backend authorization.

## Development Notes

- Local development uses SQLite by default; production settings support PostgreSQL.
- The backend has a dedicated database schema reference in [`backend/DATABASE_SCHEMA.md`](backend/DATABASE_SCHEMA.md).
- Redis/Celery configuration is available for background tasks.
- Run frontend lint checks with `npm run lint` from the `frontend/` directory.

## Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature`.
3. Make and test your changes.
4. Commit your work: `git commit -m "Add your feature"`.
5. Push the branch and open a pull request.

## License

No license file is currently included in this repository. Unless a license is added, the project is not explicitly licensed for reuse or redistribution.
