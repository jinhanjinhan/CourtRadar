from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.listings import repository
from app.modules.listings.schemas import ParsedListingCreate


async def create_parsed_listing(session: AsyncSession, payload: ParsedListingCreate):
    return await repository.create_parsed_listing(
        session,
        source_channel=payload.source_channel,
        raw_text=payload.raw_text,
        venue=payload.venue,
        listing_date=payload.listing_date,
        start_time=payload.start_time,
        end_time=payload.end_time,
        price=payload.price,
    )


async def list_parsed_listings(session: AsyncSession):
    return await repository.list_parsed_listings(session)


async def get_parsed_listing(session: AsyncSession, listing_id: int):
    return await repository.get_parsed_listing(session, listing_id)
