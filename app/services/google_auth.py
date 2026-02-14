"""Google ID token verification helpers."""

from __future__ import annotations

import json
import time
from urllib.request import urlopen

from jose import JWTError, jwt

from app.core.config import settings
from app.core.exceptions import ClientError

_JWKS_CACHE: dict[str, object] = {"expires_at": 0.0, "keys": []}


def _load_google_jwks() -> list[dict[str, object]]:
    now = time.time()
    if now < float(_JWKS_CACHE["expires_at"]):
        return _JWKS_CACHE["keys"]  # type: ignore[return-value]

    with urlopen(settings.google_jwks_url, timeout=5) as response:  # noqa: S310 - trusted config URL
        payload = json.loads(response.read().decode("utf-8"))

    keys = payload.get("keys", [])
    _JWKS_CACHE["keys"] = keys
    _JWKS_CACHE["expires_at"] = now + 300
    return keys


def verify_google_id_token(id_token: str) -> dict[str, object]:
    """Validate a Google ID token and return claims payload."""

    if not settings.google_client_ids:
        raise ClientError(
            "Google login is not configured",
            code="GOOGLE_LOGIN_DISABLED",
            status_code=503,
        )

    try:
        header = jwt.get_unverified_header(id_token)
    except JWTError as exc:
        raise ClientError("Malformed Google ID token", code="INVALID_GOOGLE_TOKEN", status_code=401) from exc

    kid = header.get("kid")
    if not kid:
        raise ClientError("Malformed Google token header", code="INVALID_GOOGLE_TOKEN", status_code=401)

    keys = _load_google_jwks()
    matching_key = next((key for key in keys if key.get("kid") == kid), None)
    if not matching_key:
        raise ClientError("Unknown Google token key", code="INVALID_GOOGLE_TOKEN", status_code=401)

    try:
        payload = jwt.decode(
            id_token,
            matching_key,
            algorithms=["RS256"],
            audience=settings.google_client_ids,
            issuer=settings.google_issuer,
        )
    except JWTError as exc:
        raise ClientError("Invalid Google ID token", code="INVALID_GOOGLE_TOKEN", status_code=401) from exc

    if payload.get("email_verified") is not True:
        raise ClientError("Google email is not verified", code="UNVERIFIED_GOOGLE_EMAIL", status_code=403)

    return payload
