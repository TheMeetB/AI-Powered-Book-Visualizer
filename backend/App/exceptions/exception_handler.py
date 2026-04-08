import traceback

from fastapi import HTTPException, status, Request
from fastapi.responses import JSONResponse
from loguru import logger

from ..dto import StandardResponse


# Custom Exceptions inheriting from HTTPException
class BadRequestException(HTTPException):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class UnauthorizedException(HTTPException):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class ForbiddenException(HTTPException):
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class NotFoundException(HTTPException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class UnprocessableEntityException(HTTPException):
    def __init__(self, detail: str = "Unprocessable entity"):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)


class InternalServerErrorException(HTTPException):
    def __init__(self, detail: str = "Internal server error"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


class ServiceUnavailableException(HTTPException):
    def __init__(self, detail: str = "Service unavailable"):
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)


# Centralized Exception Handlers
# noinspection PyUnusedLocal
async def handle_custom_http_exception(request: Request, exc: HTTPException):
    """Handle custom HTTP exceptions with logging and standardized response."""
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    response = StandardResponse(
        success=False,
        status_code=exc.status_code,
        message=exc.detail,
        data=None
    )
    return JSONResponse(status_code=exc.status_code, content=response.dict())


# noinspection PyUnusedLocal
async def handle_generic_exception(request: Request, exc: Exception):
    """Handle unexpected exceptions with detailed logging."""
    error_detail = "An unexpected error occurred"
    logger.error(f"Unexpected Error: {str(exc)}\n{traceback.format_exc()}")
    response = StandardResponse(
        success=False,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message=error_detail,
        data=None
    )
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=response.dict())


# Register exception handlers with FastAPI app
def register_exception_handlers(app):
    """Register all exception handlers to the FastAPI app."""
    handlers = [
        (BadRequestException, handle_custom_http_exception), # Custom HTTP exceptions
        (UnauthorizedException, handle_custom_http_exception),
        (ForbiddenException, handle_custom_http_exception),
        (NotFoundException, handle_custom_http_exception),
        (UnprocessableEntityException, handle_custom_http_exception),
        (InternalServerErrorException, handle_custom_http_exception),
        (ServiceUnavailableException, handle_custom_http_exception),
        (HTTPException, handle_custom_http_exception), # Generic HTTPException catch-all
        (Exception, handle_generic_exception), # Unexpected exceptions
    ]
    for exception_class, handler in handlers:
        app.add_exception_handler(exception_class, handler)