from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ParsedListing


async def create_parsed_listing(
    session: AsyncSession,
    *,
    source_channel: str,
    raw_text: str,
    venue: str,
    listing_date: str,
    start_time,
    end_time,
    price,
) -> ParsedListing:
    listing = ParsedListing(
        source_channel=source_channel,
        raw_text=raw_text,
        venue=venue,
        listing_date=listing_date,
        start_time=start_time,
        end_time=end_time,
        price=price,
    )
    session.add(listing)
    await session.commit()
    await session.refresh(listing)
    return listing


async def list_parsed_listings(session: AsyncSession) -> list[ParsedListing]:
    result = await session.execute(
        select(ParsedListing).order_by(ParsedListing.id.desc())
    )
    return list(result.scalars().all())


async def get_parsed_listing(session: AsyncSession, listing_id: int):
    return await session.get(ParsedListing, listing_id)
