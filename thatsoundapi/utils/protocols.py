from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    """Error detail for API responses."""

    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")


class APIResponse(BaseModel, Generic[T]):
    """Unified API response model."""

    success: bool = Field(..., description="Whether the request was successful")
    data: T | None = Field(default=None, description="Response data")
    error: ErrorDetail | None = Field(default=None, description="Error details")
    message: str | None = Field(default=None, description="Optional message")


class SuccessResponse(APIResponse[T]):
    """Success response model."""

    success: bool = Field(default=True, description="Always True for success responses")
    data: T = Field(..., description="Response data")
    error: None = Field(default=None, description="Always None for success responses")


class ErrorResponse(APIResponse[None]):
    """Error response model."""

    success: bool = Field(default=False, description="Always False for error responses")
    data: None = Field(default=None, description="Always None for error responses")
    error: ErrorDetail = Field(..., description="Error details")
