"""Service helpers for user persistence and retrieval."""

from datetime import UTC, datetime

import aiosqlite

from app.core.exceptions import ClientError


class UserService:
    """Encapsulates CRUD operations for users."""

    @staticmethod
    async def get_by_email(conn: aiosqlite.Connection, email: str) -> aiosqlite.Row | None:
        cursor = await conn.execute("SELECT * FROM users WHERE email = ?", (email,))
        return await cursor.fetchone()

    @staticmethod
    async def get_by_id(conn: aiosqlite.Connection, user_id: int) -> aiosqlite.Row | None:
        cursor = await conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return await cursor.fetchone()

    @staticmethod
    async def get_by_google_sub(conn: aiosqlite.Connection, google_sub: str) -> aiosqlite.Row | None:
        cursor = await conn.execute("SELECT * FROM users WHERE google_sub = ?", (google_sub,))
        return await cursor.fetchone()

    @staticmethod
    async def create_local_user(
        conn: aiosqlite.Connection,
        *,
        email: str,
        username: str,
        password_hash: str,
    ) -> aiosqlite.Row:
        now = datetime.now(UTC).isoformat()
        try:
            await conn.execute(
                """
                INSERT INTO users (email, username, password_hash, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (email, username, password_hash, now, now),
            )
            await conn.commit()
        except aiosqlite.IntegrityError as exc:
            raise ClientError(
                "Email or username already exists",
                code="USER_ALREADY_EXISTS",
                status_code=409,
            ) from exc
        user = await UserService.get_by_email(conn, email)
        assert user is not None
        return user

    @staticmethod
    async def create_google_user(
        conn: aiosqlite.Connection,
        *,
        email: str,
        username: str,
        google_sub: str,
    ) -> aiosqlite.Row:
        now = datetime.now(UTC).isoformat()
        base_username = username
        attempt = 0
        while True:
            candidate = base_username if attempt == 0 else f"{base_username}{attempt}"
            try:
                await conn.execute(
                    """
                    INSERT INTO users (email, username, google_sub, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (email, candidate, google_sub, now, now),
                )
                await conn.commit()
                break
            except aiosqlite.IntegrityError:
                # If email or google_sub already exists concurrently, try to read it.
                existing = await UserService.get_by_email(conn, email)
                if existing:
                    return existing
                attempt += 1
                if attempt > 10:
                    raise ClientError("Unable to allocate username", code="USERNAME_CONFLICT", status_code=409)

        user = await UserService.get_by_google_sub(conn, google_sub)
        assert user is not None
        return user

    @staticmethod
    async def update_username(conn: aiosqlite.Connection, *, user_id: int, username: str) -> aiosqlite.Row:
        now = datetime.now(UTC).isoformat()
        try:
            await conn.execute(
                "UPDATE users SET username = ?, updated_at = ? WHERE id = ?",
                (username, now, user_id),
            )
            await conn.commit()
        except aiosqlite.IntegrityError as exc:
            raise ClientError("Username already in use", code="USERNAME_CONFLICT", status_code=409) from exc

        user = await UserService.get_by_id(conn, user_id)
        if user is None:
            raise ClientError("User not found", code="USER_NOT_FOUND", status_code=404)
        return user
