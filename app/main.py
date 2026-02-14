"""FastAPI application entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.error_handlers import register_exception_handlers
from app.db.database import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Initialize app resources on startup."""

    await init_db()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
register_exception_handlers(app)
app.include_router(api_router, prefix=settings.api_prefix)

