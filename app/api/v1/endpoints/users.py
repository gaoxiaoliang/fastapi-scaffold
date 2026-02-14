"""User profile endpoints requiring authentication."""

from typing import Annotated

import aiosqlite
from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.db.database import get_db
from app.schemas.user import UpdateUserRequest, UserProfileResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserProfileResponse)
async def get_me(
    current_user: Annotated[aiosqlite.Row, Depends(get_current_user)],
) -> UserProfileResponse:
    """Retrieve current user profile."""

    return UserProfileResponse(email=current_user["email"], username=current_user["username"])


@router.patch("/me", response_model=UserProfileResponse)
async def update_me(
    payload: UpdateUserRequest,
    current_user: Annotated[aiosqlite.Row, Depends(get_current_user)],
    conn: Annotated[aiosqlite.Connection, Depends(get_db)],
) -> UserProfileResponse:
    """Update current user's profile fields."""

    updated_user = await UserService.update_username(conn, user_id=current_user["id"], username=payload.username)
    return UserProfileResponse(email=updated_user["email"], username=updated_user["username"])
