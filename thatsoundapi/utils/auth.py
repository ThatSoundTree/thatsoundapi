from fastapi import Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from thatsoundapi.settings import get_settings
from thatsoundapi.utils.exceptions.app import UnauthorizedRequestError

security_scheme = HTTPBearer()


def verify_basic_auth(token: HTTPAuthorizationCredentials = Security(security_scheme)) -> str:
    """Verify auth key from Authorization header."""
    settings = get_settings()
    auth_key = token.credentials
    if auth_key != settings.AUTH_KEY.get_secret_value():
        raise UnauthorizedRequestError
    return auth_key
