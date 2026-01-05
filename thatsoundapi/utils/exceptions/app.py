from thatsoundapi.utils.exceptions.base import InternalServerError


class UnknownDatabaseError(InternalServerError):
    """Unknown database error (500)."""

    message = "Unknown database error. Please try again later"
