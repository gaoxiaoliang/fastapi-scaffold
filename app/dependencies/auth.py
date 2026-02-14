"""Authentication dependencies."""

from typing import Annotated

import aiosqlite
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exceptions import ClientError
from app.core.security import decode_access_token
from app.db.database import get_db
from app.services.user_service import UserService

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    conn: Annotated[aiosqlite.Connection, Depends(get_db)],
) -> aiosqlite.Row:
    """Resolve and return the authenticated user."""

    if credentials is None:
        raise ClientError("Authentication required", code="UNAUTHORIZED", status_code=401)

    payload = decode_access_token(credentials.credentials)
    user_id_raw = payload.get("sub")
    try:
        user_id = int(user_id_raw)
    except (TypeError, ValueError) as exc:
        raise ClientError("Invalid token subject", code="INVALID_TOKEN", status_code=401) from exc

    user = await UserService.get_by_id(conn, user_id)
    if user is None:
        raise ClientError("User not found", code="USER_NOT_FOUND", status_code=404)
    return user
