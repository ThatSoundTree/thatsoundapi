from fastapi import APIRouter

integrations_router = APIRouter(tags=["Integrations"])

@integrations_router.get("/spotify")
async def get_integrations(hgramid: str):
    pass
