from datetime import time
from unittest.mock import AsyncMock, patch

import pytest

from app.modules.listings.schemas import ParsedListingCreate
from app.modules.listings.service import create_parsed_listing, get_parsed_listing, list_parsed_listings
from tests.factories import make_listing


_LISTING_PAYLOAD = ParsedListingCreate(
    source_channel="sg_badminton",
    raw_text="WTS badminton court $15",
    venue="Test Venue",
    listing_date="2024-06-15",
    start_time=time(20, 0),
    end_time=time(22, 0),
    price=15.0,
)


async def test_create_parsed_listing_success():
    listing = make_listing()
    session = AsyncMock()
    with patch(
        "app.modules.listings.service.repository.create_parsed_listing", new_callable=AsyncMock
    ) as mock_create:
        mock_create.return_value = listing
        result = await create_parsed_listing(session, _LISTING_PAYLOAD)
    assert result == listing
    mock_create.assert_called_once()


async def test_create_parsed_listing_passes_all_fields():
    listing = make_listing()
    session = AsyncMock()
    with patch(
        "app.modules.listings.service.repository.create_parsed_listing", new_callable=AsyncMock
    ) as mock_create:
        mock_create.return_value = listing
        await create_parsed_listing(session, _LISTING_PAYLOAD)
    _, kwargs = mock_create.call_args
    assert kwargs["source_channel"] == "sg_badminton"
    assert kwargs["venue"] == "Test Venue"
    assert kwargs["price"] == 15.0


async def test_list_parsed_listings_returns_all():
    listings = [make_listing(id=1), make_listing(id=2)]
    session = AsyncMock()
    with patch(
        "app.modules.listings.service.repository.list_parsed_listings", new_callable=AsyncMock
    ) as mock_list:
        mock_list.return_value = listings
        result = await list_parsed_listings(session)
    assert result == listings


async def test_list_parsed_listings_empty():
    session = AsyncMock()
    with patch(
        "app.modules.listings.service.repository.list_parsed_listings", new_callable=AsyncMock
    ) as mock_list:
        mock_list.return_value = []
        result = await list_parsed_listings(session)
    assert result == []


async def test_get_parsed_listing_found():
    listing = make_listing(id=5)
    session = AsyncMock()
    with patch(
        "app.modules.listings.service.repository.get_parsed_listing", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = listing
        result = await get_parsed_listing(session, 5)
    assert result == listing
    mock_get.assert_called_once_with(session, 5)


async def test_get_parsed_listing_not_found_returns_none():
    session = AsyncMock()
    with patch(
        "app.modules.listings.service.repository.get_parsed_listing", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = None
        result = await get_parsed_listing(session, 999)
    assert result is None


async def test_create_parsed_listing_without_price():
    listing = make_listing(price=None)
    session = AsyncMock()
    with patch(
        "app.modules.listings.service.repository.create_parsed_listing", new_callable=AsyncMock
    ) as mock_create:
        mock_create.return_value = listing
        payload = ParsedListingCreate(
            source_channel="sg_badminton",
            raw_text="WTS badminton court",
            venue="Venue",
            listing_date="2024-06-15",
            start_time=time(20, 0),
            end_time=time(22, 0),
        )
        result = await create_parsed_listing(session, payload)
    assert result.price is None
