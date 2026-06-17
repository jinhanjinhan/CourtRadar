from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import db_session
from app.db.models import AlertPreference
from app.modules.listings.schemas import ParsedListingCreate, ParsedListingRead
from app.modules.listings.service import create_parsed_listing, get_parsed_listing, list_parsed_listings
from app.schemas.common import CreatedResponse
from app.services.matching.engine import listing_matches_alert


router = APIRouter(prefix="", tags=["listings"])


@router.post("/parsed-listings", response_model=CreatedResponse, status_code=status.HTTP_201_CREATED)
async def create_parsed_listing_route(
    payload: ParsedListingCreate,
    session: AsyncSession = Depends(db_session),
) -> CreatedResponse:
    listing = await create_parsed_listing(session, payload)
    return CreatedResponse(id=listing.id, created_at=listing.created_at)


@router.get("/parsed-listings", response_model=list[ParsedListingRead])
async def list_parsed_listings_route(session: AsyncSession = Depends(db_session)) -> list[ParsedListingRead]:
    listings = await list_parsed_listings(session)
    return [ParsedListingRead.model_validate(listing) for listing in listings]


@router.get("/parsed-listings/{listing_id}/matches")
async def match_listing_route(listing_id: int, session: AsyncSession = Depends(db_session)) -> dict[str, object]:
    listing = await get_parsed_listing(session, listing_id)
    if listing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="listing not found")

    result = await session.execute(select(AlertPreference).where(AlertPreference.is_active.is_(True)))
    matches = [alert for alert in result.scalars().all() if listing_matches_alert(listing, alert)]

    return {
        "listing_id": listing.id,
        "match_count": len(matches),
        "matched_alert_ids": [alert.id for alert in matches],
    }
