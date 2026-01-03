from fastapi import APIRouter, Depends, status

from thatsoundapi.api.v1.models.users import UserIntegrationsResponse
from thatsoundapi.db.connection import Transaction
from thatsoundapi.db.dependencies import get_transaction
from thatsoundapi.services.integrations_service import user_integrations_service

user_router = APIRouter(tags=["Users"])


@user_router.get(
    "/{hgramid}/integrations",
    response_model=UserIntegrationsResponse,
    status_code=status.HTTP_200_OK,
)
async def user_integrations(
    hgramid: str,
    _: Transaction = Depends(get_transaction),
) -> UserIntegrationsResponse:
    """Get user integrations status."""

    response = await user_integrations_service(hgramid=hgramid)
    return response
