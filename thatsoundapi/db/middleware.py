from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from thatsoundapi.db.connection import Transaction


class TransactionMiddleware(BaseHTTPMiddleware):
    """Middleware for automatic transaction management per request.

    Automatically wraps each request in a database transaction.
    This ensures one transaction per HTTP request (Unit of Work pattern).

    The transaction is committed on successful response (2xx, 3xx status codes)
    and rolled back on errors (4xx, 5xx status codes).

    Usage:
        app.add_middleware(TransactionMiddleware)

    Note:
        This approach makes transactions implicit - you don't need to
        add transaction dependency to each route. However, it's less
        explicit and flexible than using dependencies.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Process request with automatic transaction management.

        Args:
            request: FastAPI request object
            call_next: Next middleware or route handler

        Returns:
            Response from route handler
        """
        # Skip transaction for health checks and static endpoints
        if request.url.path in ("/health", "/", "/docs", "/openapi.json", "/redoc"):
            return await call_next(request)

        async with Transaction():
            response = await call_next(request)

            # Transaction will be committed on success (no exception)
            # or rolled back on exception (handled by Transaction.__aexit__)
            return response
