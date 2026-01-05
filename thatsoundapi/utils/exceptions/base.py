from fastapi import status


def get_error_code_from_status_code(status_code: int) -> str:
    """Get error code from HTTP status code."""
    error_codes = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        500: "INTERNAL_SERVER_ERROR",
        501: "NOT_IMPLEMENTED",
    }
    return error_codes.get(status_code, "UNKNOWN_ERROR")


class BaseAPIException(Exception):
    """Base exception for all API exceptions."""

    def __init__(self, code: int | None = None, error: str | None = None) -> None:
        super().__init__()
        if hasattr(self, 'status_code') and hasattr(self, 'detail'):
            return

        # Use provided arguments or fall back to class attributes
        cls = type(self)
        if code is not None and error is not None:
            self.status_code = code
            self.detail = error
        elif hasattr(cls, 'status_code') and hasattr(cls, 'message'):
            self.status_code = cls.status_code
            self.detail = cls.message

    def __new__(cls, *args, **kwargs):
        # Allow using class without parentheses: raise SomeError
        if not args and not kwargs and hasattr(cls, 'status_code') and hasattr(cls, 'message'):
            instance = super().__new__(cls)
            instance.status_code = cls.status_code
            instance.detail = cls.message
            return instance
        return super().__new__(cls)


class BadRequestError(BaseAPIException):
    """Bad request error (400)."""

    status_code = status.HTTP_400_BAD_REQUEST
    message = "Bad request"


class UnauthorizedError(BaseAPIException):
    """Unauthorized error (401)."""

    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Unauthorized"


class NotFoundError(BaseAPIException):
    """Not found error (404)."""

    status_code = status.HTTP_404_NOT_FOUND
    message = "Not Found"


class InternalServerError(BaseAPIException):
    """Internal server error (500)."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = "Internal server error"
