"""Global exception handlers for unified error responses."""

import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import AppError, ClientError, ServerError

logger = logging.getLogger(__name__)


def _error_payload(code: str, message: str, details: object | None = None) -> dict[str, object]:
    return {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "details": details,
        },
    }


def register_exception_handlers(app: FastAPI) -> None:
    """Attach application-wide exception handlers."""

    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_payload(exc.code, exc.message, exc.details),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        client_error = ClientError(
            "Request validation failed",
            code="VALIDATION_ERROR",
            status_code=422,
            details={"errors": exc.errors()},
        )
        return JSONResponse(
            status_code=client_error.status_code,
            content=_error_payload(client_error.code, client_error.message, client_error.details),
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
        client_error = ClientError(
            str(exc.detail),
            code="HTTP_ERROR",
            status_code=exc.status_code,
        )
        return JSONResponse(
            status_code=client_error.status_code,
            content=_error_payload(client_error.code, client_error.message),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception: %s", exc)
        server_error = ServerError()
        return JSONResponse(
            status_code=server_error.status_code,
            content=_error_payload(server_error.code, server_error.message),
        )
