from thatsoundapi.utils.exceptions.base import BadRequestError, UnauthorizedError


class InvalidSpotifyOAuthStateError(BadRequestError):
    """Invalid or expired OAuth state error (400)."""

    message = "Invalid or expired Spotify OAuth state"


class SpotifyExchangeTokenError(BadRequestError):
    """Spotify exchange token error (400)."""

    message = "Failed to exchange spotify token"


class SpotifyTokenError(BadRequestError):
    """Spotify token error (400)."""

    message = "Failed to make /me request. Do you have BETA access?"


class NoSpotifyIntegrationError(UnauthorizedError):
    """No Spotify integration error (401)."""

    message = "Spotify integration doesn't exist"


class RefreshSpotifyTokenError(UnauthorizedError):
    """Refresh Spotify token error (401)."""

    message = "Failed to refresh Spotify token"


class UnknownSpotifyAPIError(BadRequestError):
    """Unknown spotify API error (400)."""

    message = "Unknown Spotify API error. Please try again later"
