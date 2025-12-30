from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger

from thatsoundapi.api.v1.routes.sounds import sounds_router
from thatsoundapi.api.v1.routes.spotify import spotify_router
from thatsoundapi.api.v1.routes.users import user_router
from thatsoundapi.core.exceptions import BaseAPIException, get_error_code_from_status_code
from thatsoundapi.core.responses import ErrorDetail, ErrorResponse
from thatsoundapi.db.redis import RedisClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager.

    Handles startup and shutdown events.

    Args:
        app: FastAPI application instance
    """
    # Startup
    logger.info("Starting application...")
    await RedisClient.connect()
    yield
    # Shutdown
    logger.info("Shutting down application...")
    await RedisClient.disconnect()


app = FastAPI(
    title="That Sound API",
    description="That Sound REST API",
    version="0.1.0",
    lifespan=lifespan,
)

# Register routers
app.include_router(sounds_router, prefix="/api/v1/sounds", tags=["Sounds"])
app.include_router(user_router, prefix="/api/v1/users", tags=["Users"])
app.include_router(spotify_router, prefix="/api/v1/spotify", tags=["Spotify"])


@app.exception_handler(BaseAPIException)
async def api_exception_handler(request: Request, exc: BaseAPIException) -> JSONResponse:
    """Handle custom API exceptions.

    Args:
        request: FastAPI request object
        exc: Custom API exception

    Returns:
        JSONResponse with unified error format
    """
    logger.error(
        "API exception: %s at %s [%s]",
        exc.detail,
        request.url.path,
        request.method,
    )

    error_response = ErrorResponse(
        error=ErrorDetail(
            code=get_error_code_from_status_code(exc.status_code),
            message=exc.detail,
        ),
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(exclude_none=True),
        headers=exc.headers,
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions.

    Args:
        request: FastAPI request object
        exc: Exception instance

    Returns:
        JSONResponse with unified error format
    """
    logger.exception(
        "Unexpected error at %s [%s]",
        request.url.path,
        request.method,
    )

    error_response = ErrorResponse(
        error=ErrorDetail(
            code="INTERNAL_SERVER_ERROR",
            message="Internal server error",
        ),
    )

    return JSONResponse(
        status_code=500,
        content=error_response.model_dump(exclude_none=True),
    )


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        Health status
    """
    return {"status": "healthy"}


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint.

    Returns:
        API information
    """
    return {"message": "That Sound API", "version": "0.1.0"}
