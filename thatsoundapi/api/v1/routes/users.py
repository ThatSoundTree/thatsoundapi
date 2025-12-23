from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from thatsoundapi.api.v1.models.users import User
from thatsoundapi.core.exceptions import BadRequestException
from thatsoundapi.core.responses import SuccessResponse, create_success_response
from thatsoundapi.db.connection import Transaction
from thatsoundapi.db.dependencies import get_transaction
from thatsoundapi.services.user_service import mention_user as mention_user_service

user_router = APIRouter(tags=["Users"])


@user_router.post(
    "/{htelegram_id}",
    response_model=SuccessResponse[User],
)
async def mention_user(
    htelegram_id: str,
    _: Transaction = Depends(get_transaction),
) -> SuccessResponse[User] | JSONResponse:
    """Get or create user by hashed Telegram ID."""
    if not htelegram_id or not htelegram_id.strip():
        raise BadRequestException("htelegram_id cannot be empty")

    user_db, is_new, integrations = await mention_user_service(htelegram_id)
    user_data = User.model_validate(user_db)
    user_data.integrations = integrations

    response_data = create_success_response(
        data=user_data,
        message="User created successfully" if is_new else None,
    )

    status_code = status.HTTP_201_CREATED if is_new else status.HTTP_200_OK
    return JSONResponse(
        status_code=status_code,
        content=response_data.model_dump(mode="json", exclude_none=True),
    )
