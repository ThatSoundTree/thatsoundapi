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

    def __init__(self, code: int, error: str) -> None:
        super().__init__()
        self.status_code = code
        self.detail = error

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


class ForbiddenError(BaseAPIException):
    """Forbidden error (403)."""

    status_code = status.HTTP_403_FORBIDDEN
    message = "Forbidden"


class NotFoundError(BaseAPIException):
    """Not found error (404)."""

    status_code = status.HTTP_404_NOT_FOUND
    message = "Not Found"


class ConflictError(BaseAPIException):
    """Conflict error (409)."""

    status_code = status.HTTP_409_CONFLICT
    message = "Conflict"


class InternalServerError(BaseAPIException):
    """Internal server error (500)."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = "Internal server error"


class NotImplementedError(BaseAPIException):
    """Not implemented error (501)."""

    status_code = status.HTTP_501_NOT_IMPLEMENTED
    message = "Not implemented"


class DatabaseError(InternalServerError):
    """Database error (500)."""

    message = "Database error"


class HgramidNotFoundError(NotFoundError):
    """ Telegram ID error (400)."""

    message = "Hgramid not found"


class InvalidOAuthStateError(BadRequestError):
    """Invalid or expired OAuth state error (400)."""

    message = "Invalid or expired OAuth state"
