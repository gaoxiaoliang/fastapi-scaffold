# fastapi-scaffold

A FastAPI scaffold focused on JWT-based authentication APIs.

## Tech Stack

- Python 3.12
- `uvicorn[standard]==0.40.0`
- `fastapi[standard]==0.128.7`
- `pydantic==2.12.5`
- `email-validator==2.3.0`
- `pydantic-settings==2.12.0`
- `aiosqlite==0.22.1`
- `python-jose==3.5.0`
- `bcrypt==5.0.0`

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload
```

## Environment Variables

| Name | Default | Description |
|---|---|---|
| `APP_NAME` | `FastAPI Scaffold` | App title |
| `API_PREFIX` | `/api/v1` | API prefix |
| `DATABASE_URL` | `sqlite+aiosqlite:///./app.db` | SQLite database URL |
| `JWT_SECRET_KEY` | `change-me-in-production` | JWT signing secret |
| `JWT_ALGORITHM` | `HS256` | JWT algorithm |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Access token lifetime |
| `GOOGLE_CLIENT_IDS` | `[]` | Allowed Google OAuth client IDs |
| `GOOGLE_ISSUER` | `https://accounts.google.com` | Expected Google issuer |
| `GOOGLE_JWKS_URL` | `https://www.googleapis.com/oauth2/v3/certs` | Google JWKS URL |

`GOOGLE_CLIENT_IDS` should be provided as JSON array in `.env`, for example:

```env
GOOGLE_CLIENT_IDS=["your-web-client-id.apps.googleusercontent.com"]
```

## API Overview

Public endpoints:

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/google`

Authenticated endpoints (Bearer token required):

- `GET /api/v1/users/me`
- `PATCH /api/v1/users/me`

All error responses follow a unified format:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": {}
  }
}
```
