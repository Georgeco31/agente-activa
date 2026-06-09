import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import ApiError, ErrorCode
from app.schemas.error import ErrorDetail, ErrorResponse

logger = logging.getLogger(__name__)


def _error_response(
    *,
    status_code: int,
    code: ErrorCode,
    message: str,
    details: dict[str, Any] | None = None,
) -> JSONResponse:
    response = ErrorResponse(
        error=ErrorDetail(
            code=code.value,
            message=message,
            details=details or {},
        )
    )
    return JSONResponse(status_code=status_code, content=response.model_dump(mode="json"))


async def api_error_handler(_request: Request, exc: ApiError) -> JSONResponse:
    return _error_response(
        status_code=exc.status_code,
        code=exc.code,
        message=exc.message,
        details=exc.details,
    )


async def validation_error_handler(
    _request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    errors = [
        {
            "field": ".".join(str(part) for part in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        }
        for error in exc.errors()
    ]
    return _error_response(
        status_code=422,
        code=ErrorCode.VALIDATION_ERROR,
        message="Request validation failed.",
        details={"errors": errors},
    )


async def http_error_handler(
    _request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    if exc.status_code >= 500:
        return _error_response(
            status_code=exc.status_code,
            code=ErrorCode.INTERNAL_SERVER_ERROR,
            message="Internal server error.",
        )

    code = (
        ErrorCode.RESOURCE_NOT_FOUND
        if exc.status_code == 404
        else ErrorCode.BUSINESS_RULE_ERROR
    )
    message = exc.detail if isinstance(exc.detail, str) else "Request could not be processed."
    return _error_response(status_code=exc.status_code, code=code, message=message)


async def unexpected_error_handler(_request: Request, exc: Exception) -> JSONResponse:
    logger.error(
        "Unhandled API exception.",
        exc_info=(type(exc), exc, exc.__traceback__),
    )
    return _error_response(
        status_code=500,
        code=ErrorCode.INTERNAL_SERVER_ERROR,
        message="Internal server error.",
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ApiError, api_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_error_handler)
    app.add_exception_handler(Exception, unexpected_error_handler)
