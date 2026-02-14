"""Database connectivity and schema bootstrap."""

from collections.abc import AsyncGenerator

import aiosqlite

from app.core.config import settings
from app.core.exceptions import ServerError


def _sqlite_path() -> str:
    prefix = "sqlite+aiosqlite:///"
    if not settings.database_url.startswith(prefix):
        raise ServerError("Only sqlite+aiosqlite URLs are supported", code="DB_CONFIG_ERROR")
    return settings.database_url.removeprefix(prefix)


async def get_db() -> AsyncGenerator[aiosqlite.Connection, None]:
    """Yield a SQLite connection for request scope."""

    conn = await aiosqlite.connect(_sqlite_path())
    conn.row_factory = aiosqlite.Row
    try:
        yield conn
    finally:
        await conn.close()


async def init_db() -> None:
    """Initialize required database tables."""

    async with aiosqlite.connect(_sqlite_path()) as conn:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT,
                google_sub TEXT UNIQUE,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        await conn.commit()
