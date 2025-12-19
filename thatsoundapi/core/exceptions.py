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

    def __init__(
        self,
        detail: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.status_code = status_code
        self.detail = detail
        self.headers = headers
        super().__init__(self.detail)


class BadRequestException(BaseAPIException):
    """Bad request error (400)."""

    def __init__(
        self,
        detail: str = "Bad request",
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_400_BAD_REQUEST,
            headers=headers,
        )


class UnauthorizedException(BaseAPIException):
    """Unauthorized error (401)."""

    def __init__(
        self,
        detail: str = "Unauthorized",
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers=headers,
        )


class ForbiddenException(BaseAPIException):
    """Forbidden error (403)."""

    def __init__(
        self,
        detail: str = "Forbidden",
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_403_FORBIDDEN,
            headers=headers,
        )


class NotFoundException(BaseAPIException):
    """Not found error (404)."""

    def __init__(
        self,
        detail: str = "Not found",
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_404_NOT_FOUND,
            headers=headers,
        )


class ConflictException(BaseAPIException):
    """Conflict error (409)."""

    def __init__(
        self,
        detail: str = "Conflict",
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_409_CONFLICT,
            headers=headers,
        )


class InternalServerError(BaseAPIException):
    """Internal server error (500)."""

    def __init__(
        self,
        detail: str = "Internal server error",
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers=headers,
        )


class NotImplementedException(BaseAPIException):
    """Not implemented error (501)."""

    def __init__(
        self,
        detail: str = "Not implemented",
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            headers=headers,
        )


class DatabaseError(InternalServerError):
    """Database error (500)."""

    def __init__(
        self,
        detail: str = "Database error",
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(detail=detail, headers=headers)
