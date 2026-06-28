from fastapi import APIRouter

from app.modules.alerts.router import router as alerts_router
from app.modules.listings.router import router as listings_router
from app.modules.users.router import router as users_router

router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


router.include_router(users_router)
router.include_router(alerts_router)
router.include_router(listings_router)
