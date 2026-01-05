from thatsoundapi.utils.exceptions.base import InternalServerError, UnauthorizedError


class UnknownDatabaseError(InternalServerError):
    """Unknown database error (500)."""

    message = "Unknown database error. Please try again later"


class UnauthorizedRequestError(UnauthorizedError):
    """Unauthorized request error (401)."""

    message = "Unauthorized request error. Please use basic authentication first"
