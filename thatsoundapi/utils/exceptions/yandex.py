from thatsoundapi.utils.exceptions.base import BadRequestError, UnauthorizedError


class YandexTokenError(BadRequestError):
    """Yandex token error (400)."""

    message = "Invalid yandex token. Can't GET /account/status"


class NoYandexMusicIntegrationError(UnauthorizedError):
    """No Yandex Music integration error (401)."""

    message = "Yandex Music integration doesn't exist"


class UnknownYandexMusicAPIError(BadRequestError):
    """Unknown yandex music API error (400)."""

    message = "Unknown Yandex Music API error. Please try again later"
