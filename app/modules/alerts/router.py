from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import db_session
from app.modules.alerts.schemas import AlertPreferenceCreate, AlertPreferenceRead
from app.modules.alerts.service import create_alert_preference, list_alert_preferences
from app.schemas.common import CreatedResponse


router = APIRouter(prefix="", tags=["alerts"])


@router.post(
    "/alert-preferences",
    response_model=CreatedResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_alert_preference_route(
    payload: AlertPreferenceCreate,
    session: AsyncSession = Depends(db_session),
) -> CreatedResponse:
    try:
        alert = await create_alert_preference(session, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    return CreatedResponse(id=alert.id, created_at=alert.created_at)


@router.get("/alert-preferences", response_model=list[AlertPreferenceRead])
async def list_alert_preferences_route(
    user_id: Optional[int] = None,
    session: AsyncSession = Depends(db_session),
) -> list[AlertPreferenceRead]:
    alerts = await list_alert_preferences(session, user_id=user_id)
    return [AlertPreferenceRead.model_validate(alert) for alert in alerts]
