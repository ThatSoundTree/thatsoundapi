from thatsoundapi.utils.exceptions.base import BadRequestError


class YandexTokenError(BadRequestError):
    """Yandex token error (400)."""

    message = "Invalid yandex token. Can't GET /account/status"
