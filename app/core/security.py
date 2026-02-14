"""Security helpers for password hashing and JWT token management."""

from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings
from app.core.exceptions import ClientError


def hash_password(password: str) -> str:
    """Hash a plain-text password using bcrypt."""

    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a plain-text password against a stored hash."""

    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_access_token(subject: str, expires_minutes: int | None = None) -> str:
    """Issue an access JWT token for a user subject."""

    expire_delta = timedelta(minutes=expires_minutes or settings.jwt_access_token_expire_minutes)
    payload = {
        "sub": subject,
        "exp": datetime.now(UTC) + expire_delta,
        "type": "access",
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate an access token."""

    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise ClientError("Invalid or expired token", code="INVALID_TOKEN", status_code=401) from exc

    if payload.get("type") != "access" or not payload.get("sub"):
        raise ClientError("Invalid token payload", code="INVALID_TOKEN_PAYLOAD", status_code=401)
    return payload
