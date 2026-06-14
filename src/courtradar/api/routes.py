from datetime import time
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from courtradar.api.deps import db_session
from courtradar.db.models import AlertPreference, ParsedListing, User
from courtradar.schemas.alert import AlertPreferenceCreate, AlertPreferenceRead
from courtradar.schemas.listing import ParsedListingCreate, ParsedListingRead
from courtradar.schemas.common import CreatedResponse
from courtradar.services.matching.engine import listing_matches_alert

router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, str]:
    # Simple liveness check for smoke tests and deployment probes.
    return {"status": "ok"}


@router.post("/users", response_model=CreatedResponse, status_code=status.HTTP_201_CREATED)
async def create_user(payload: Dict[str, str], session: AsyncSession = Depends(db_session)) -> CreatedResponse:
    # Minimal starter endpoint for creating an application user.
    email = payload.get("email", "").strip().lower()
    display_name = payload.get("display_name", "").strip()
    telegram_chat_id = payload.get("telegram_chat_id")

    if not email or not display_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="email and display_name are required")

    existing_user = await session.scalar(select(User).where(User.email == email))
    if existing_user is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="email already exists")

    user = User(email=email, display_name=display_name, telegram_chat_id=telegram_chat_id)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return CreatedResponse(id=user.id, created_at=user.created_at)


@router.get("/users/{user_id}")
async def get_user(user_id: int, session: AsyncSession = Depends(db_session)) -> Dict[str, object]:
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")

    return {
        "id": user.id,
        "email": user.email,
        "display_name": user.display_name,
        "telegram_chat_id": user.telegram_chat_id,
    }


@router.post("/alert-preferences", response_model=CreatedResponse, status_code=status.HTTP_201_CREATED)
async def create_alert_preference(
    payload: AlertPreferenceCreate,
    session: AsyncSession = Depends(db_session),
) -> CreatedResponse:
    # Stores the user's matching criteria that the backend will compare against parsed listings.
    user = await session.get(User, payload.user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")

    alert = AlertPreference(
        user_id=payload.user_id,
        venue=payload.venue,
        earliest_time=payload.earliest_time,
        latest_time=payload.latest_time,
        max_price=payload.max_price,
    )
    session.add(alert)
    await session.commit()
    await session.refresh(alert)
    return CreatedResponse(id=alert.id, created_at=alert.created_at)


@router.get("/alert-preferences", response_model=list[AlertPreferenceRead])
async def list_alert_preferences(user_id: Optional[int] = None, session: AsyncSession = Depends(db_session)) -> List[AlertPreference]:
    query = select(AlertPreference)
    if user_id is not None:
        query = query.where(AlertPreference.user_id == user_id)
    result = await session.execute(query.order_by(AlertPreference.id.desc()))
    return list(result.scalars().all())


@router.post("/parsed-listings", response_model=CreatedResponse, status_code=status.HTTP_201_CREATED)
async def create_parsed_listing(
    payload: ParsedListingCreate,
    session: AsyncSession = Depends(db_session),
) -> CreatedResponse:
    # This is the first backend slice of the ingestion pipeline.
    listing = ParsedListing(
        source_channel=payload.source_channel,
        raw_text=payload.raw_text,
        venue=payload.venue,
        listing_date=payload.listing_date,
        start_time=payload.start_time,
        end_time=payload.end_time,
        price=payload.price,
    )
    session.add(listing)
    await session.commit()
    await session.refresh(listing)
    return CreatedResponse(id=listing.id, created_at=listing.created_at)


@router.get("/parsed-listings", response_model=list[ParsedListingRead])
async def list_parsed_listings(session: AsyncSession = Depends(db_session)) -> List[ParsedListing]:
    result = await session.execute(select(ParsedListing).order_by(ParsedListing.id.desc()))
    return list(result.scalars().all())


@router.get("/parsed-listings/{listing_id}/matches")
async def match_listing(listing_id: int, session: AsyncSession = Depends(db_session)) -> dict[str, object]:
    # Reuses the matching engine so you can see which saved alerts would receive a notification.
    listing = await session.get(ParsedListing, listing_id)
    if listing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="listing not found")

    result = await session.execute(select(AlertPreference).where(AlertPreference.is_active.is_(True)))
    matches = [alert for alert in result.scalars().all() if listing_matches_alert(listing, alert)]

    return {
        "listing_id": listing.id,
        "match_count": len(matches),
        "matched_alert_ids": [alert.id for alert in matches],
    }
