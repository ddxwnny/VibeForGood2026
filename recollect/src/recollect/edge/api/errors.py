"""
Shared error envelope + FastAPI exception handlers.

Implements the api-standards envelope for errors:

    { "error": { "code": "SNAKE_CASE_STRING", "message": "...", "details": [...] } }

`RecollectError` subclasses map to stable machine-readable codes so clients can
branch on them the same way across every endpoint. Validation errors from
FastAPI/Pydantic are translated to 422 with field-level details.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from recollect.core.errors import RecollectError


def _code_for(exc: RecollectError) -> str:
    name = type(exc).__name__
    if name.endswith("Error"):
        name = name[: -len("Error")]
    # CamelCase -> SNAKE_CASE
    return "".join("_" + c.lower() if c.isupper() else c for c in name).lstrip("_").upper()


def _http_code_for(status: int) -> str:
    return {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        429: "RATE_LIMITED",
        502: "UPSTREAM_ERROR",
    }.get(status, "HTTP_ERROR")


def error_body(exc: Exception, status: int) -> dict:
    if isinstance(exc, RecollectError):
        code = _code_for(exc)
    else:
        code = "INTERNAL_ERROR"
    return {
        "error": {
            "code": code,
            "message": str(exc) or "An error occurred.",
            "details": [],
        }
    }


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RecollectError)
    async def recollect_error_handler(request: Request, exc: RecollectError) -> JSONResponse:
        return JSONResponse(status_code=400, content=error_body(exc, 400))

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        # Preserve the route-set status code (403/401/404) but render the shared
        # envelope so clients always see { error: { code, message, details } }.
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": _http_code_for(exc.status_code),
                    "message": str(exc.detail),
                    "details": [],
                }
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        details = [
            {
                "loc": list(err.get("loc", [])),
                "msg": err.get("msg", ""),
                "type": err.get("type", ""),
            }
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed.",
                    "details": details,
                }
            },
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed.",
                    "details": [{"msg": e.get("msg", str(exc))} for e in exc.errors()],
                }
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": f"{type(exc).__name__}: {exc}",
                    "details": [],
                }
            },
        )

