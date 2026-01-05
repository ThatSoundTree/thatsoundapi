from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger

from thatsoundapi.api.v1.routes.callback import callback_router
from thatsoundapi.api.v1.routes.spotify import spotify_router
from thatsoundapi.api.v1.routes.users import user_router
from thatsoundapi.utils.exceptions.base import BaseAPIException, get_error_code_from_status_code
from thatsoundapi.utils.protocols import ErrorDetail, ErrorResponse

from thatsoundapi.db.redis import RedisClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager"""
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
    version="0.1.1",
    lifespan=lifespan,
)


app.include_router(user_router, prefix="/api/v1", tags=["Main"])
app.include_router(spotify_router, prefix="/api/v1/{hgramid}/integrations/spotify", tags=["Spotify"])
app.include_router(callback_router, prefix="/api/v1/callback", tags=["Callback"])

@app.exception_handler(BaseAPIException)
async def api_exception_handler(request: Request, exc: BaseAPIException) -> JSONResponse:
    """Handle custom API exceptions"""
    logger.error(
        "API exception: {} at {} [{}]",
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
        headers=getattr(exc, 'headers', None),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions"""
    logger.exception(
        "Unexpected error at {} [{}]",
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
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint"""
    return {"message": "That Sound API", "version": "0.1.1"}
