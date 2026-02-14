"""Authentication endpoints."""

from typing import Annotated

import aiosqlite
from fastapi import APIRouter, Depends, status

from app.core.exceptions import ClientError
from app.core.security import create_access_token, hash_password, verify_password
from app.db.database import get_db
from app.schemas.auth import GoogleLoginRequest, LoginRequest, RegisterRequest, TokenResponse
from app.services.google_auth import verify_google_id_token
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    conn: Annotated[aiosqlite.Connection, Depends(get_db)],
) -> TokenResponse:
    """Register a user with username, email, and password."""

    password_hash = hash_password(payload.password)
    user = await UserService.create_local_user(
        conn,
        email=payload.email,
        username=payload.username,
        password_hash=password_hash,
    )
    token = create_access_token(str(user["id"]))
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    conn: Annotated[aiosqlite.Connection, Depends(get_db)],
) -> TokenResponse:
    """Login using email and password."""

    user = await UserService.get_by_email(conn, payload.email)
    if user is None:
        raise ClientError("Invalid credentials", code="INVALID_CREDENTIALS", status_code=401)

    password_hash = user["password_hash"]
    if not password_hash or not verify_password(payload.password, password_hash):
        raise ClientError("Invalid credentials", code="INVALID_CREDENTIALS", status_code=401)

    token = create_access_token(str(user["id"]))
    return TokenResponse(access_token=token)


@router.post("/google", response_model=TokenResponse)
async def google_login(
    payload: GoogleLoginRequest,
    conn: Annotated[aiosqlite.Connection, Depends(get_db)],
) -> TokenResponse:
    """Login or register a user using a Google ID token."""

    claims = verify_google_id_token(payload.id_token)
    email = str(claims["email"])
    google_sub = str(claims["sub"])
    preferred_name = str(claims.get("name") or email.split("@")[0])

    user = await UserService.get_by_google_sub(conn, google_sub)
    if user is None:
        existing_by_email = await UserService.get_by_email(conn, email)
        if existing_by_email is not None:
            await conn.execute(
                "UPDATE users SET google_sub = ?, updated_at = datetime('now') WHERE id = ?",
                (google_sub, existing_by_email["id"]),
            )
            await conn.commit()
            user = await UserService.get_by_id(conn, existing_by_email["id"])
        else:
            user = await UserService.create_google_user(
                conn,
                email=email,
                username=preferred_name,
                google_sub=google_sub,
            )

    token = create_access_token(str(user["id"]))
    return TokenResponse(access_token=token)
