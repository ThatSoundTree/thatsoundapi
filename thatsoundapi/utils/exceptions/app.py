from thatsoundapi.utils.exceptions.base import InternalServerError, UnauthorizedError


class UnknownDatabaseError(InternalServerError):
    """Unknown database error (500)."""

    message = "Unknown database error. Please try again later"


class UnauthorizedRequestError(UnauthorizedError):
    """Unauthorized request error (401)."""

    message = "Unauthorized request error. Please use basic authentication first"


class UserNotFoundError(UnauthorizedRequestError):
    """User not found error (404)."""

    message = "User not found error. Invalid hgramid param"
