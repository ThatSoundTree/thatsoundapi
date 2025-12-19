import hashlib
import hmac

from thatsoundapi.settings import get_settings


def hash_telegram_id(telegram_id: int | str, use_sha3: bool = False) -> str:
    """Hash telegram_id using SECRET_KEY from settings."""
    secret_key = get_settings().SECRET_KEY.get_secret_value()
    algorithm = hashlib.sha3_256 if use_sha3 else hashlib.sha256
    return hmac.new(
        secret_key.encode(),
        str(telegram_id).encode(),
        algorithm,
    ).hexdigest()
