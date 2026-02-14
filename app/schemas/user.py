"""User-related request/response schemas."""

from pydantic import BaseModel, Field


class UserProfileResponse(BaseModel):
    email: str
    username: str


class UpdateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
