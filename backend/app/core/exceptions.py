from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.logging import logger
from app.core.responses import error_response


class AppException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error_code: str = "app_error",
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(message)


async def app_exception_handler(_: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            message=exc.message,
            errors={"code": exc.error_code},
        ),
    )


def _sanitize_validation_errors(errors: list) -> list:
    """Convert non-serializable objects (e.g. raw exceptions in ctx) to strings."""
    sanitized = []
    for error in errors:
        entry = dict(error)
        if "ctx" in entry:
            entry["ctx"] = {
                k: str(v) if isinstance(v, Exception) else v
                for k, v in entry["ctx"].items()
            }
        sanitized.append(entry)
    return sanitized


async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response(
            message="Request validation failed.",
            errors=_sanitize_validation_errors(exc.errors()),
        ),
    )


async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response(
            message="Internal server error.",
            errors={"code": "internal_server_error"},
        ),
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
