from datetime import time
from unittest.mock import AsyncMock, MagicMock, patch


from tests.factories import make_alert, make_listing


_CREATE_PAYLOAD = {
    "source_channel": "sg_badminton",
    "raw_text": "WTS badminton court $10",
    "venue": "Test Venue",
    "listing_date": "2024-06-15",
    "start_time": "20:00:00",
    "end_time": "22:00:00",
    "price": 10.0,
}


def test_create_parsed_listing_success(client):
    listing = make_listing(id=10)
    with patch(
        "app.modules.listings.router.create_parsed_listing", new_callable=AsyncMock
    ) as mock:
        mock.return_value = listing
        response = client.post("/parsed-listings", json=_CREATE_PAYLOAD)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 10
    assert "created_at" in data


def test_create_parsed_listing_missing_required_field_returns_422(client):
    payload = {k: v for k, v in _CREATE_PAYLOAD.items() if k != "venue"}
    response = client.post("/parsed-listings", json=payload)
    assert response.status_code == 422


def test_create_parsed_listing_without_price(client):
    listing = make_listing(price=None)
    with patch(
        "app.modules.listings.router.create_parsed_listing", new_callable=AsyncMock
    ) as mock:
        mock.return_value = listing
        payload = {k: v for k, v in _CREATE_PAYLOAD.items() if k != "price"}
        response = client.post("/parsed-listings", json=payload)
    assert response.status_code == 201


def test_list_parsed_listings_returns_all(client):
    listings = [make_listing(id=1), make_listing(id=2)]
    with patch(
        "app.modules.listings.router.list_parsed_listings", new_callable=AsyncMock
    ) as mock:
        mock.return_value = listings
        response = client.get("/parsed-listings")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["id"] == 1


def test_list_parsed_listings_empty(client):
    with patch(
        "app.modules.listings.router.list_parsed_listings", new_callable=AsyncMock
    ) as mock:
        mock.return_value = []
        response = client.get("/parsed-listings")
    assert response.status_code == 200
    assert response.json() == []


def test_match_listing_found_no_matches(client, mock_db):
    listing = make_listing(
        id=1, venue="Arena", price=10.0, start_time=time(20, 0), end_time=time(22, 0)
    )
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute = AsyncMock(return_value=mock_result)
    with patch(
        "app.modules.listings.router.get_parsed_listing", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = listing
        response = client.get("/parsed-listings/1/matches")
    assert response.status_code == 200
    data = response.json()
    assert data["listing_id"] == 1
    assert data["match_count"] == 0
    assert data["matched_alert_ids"] == []


def test_match_listing_found_with_matches(client, mock_db):
    listing = make_listing(
        id=2, venue="Arena", price=10.0, start_time=time(20, 0), end_time=time(22, 0)
    )
    # Alert that matches the listing
    alert = make_alert(
        id=5,
        venue="Arena",
        max_price=15.0,
        earliest_time=time(19, 0),
        latest_time=time(23, 0),
    )
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [alert]
    mock_db.execute = AsyncMock(return_value=mock_result)
    with patch(
        "app.modules.listings.router.get_parsed_listing", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = listing
        response = client.get("/parsed-listings/2/matches")
    assert response.status_code == 200
    data = response.json()
    assert data["listing_id"] == 2
    assert data["match_count"] == 1
    assert 5 in data["matched_alert_ids"]


def test_match_listing_not_found_returns_404(client):
    with patch(
        "app.modules.listings.router.get_parsed_listing", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = None
        response = client.get("/parsed-listings/999/matches")
    assert response.status_code == 404
    assert response.json()["detail"] == "listing not found"


def test_match_listing_alert_price_too_high_excluded(client, mock_db):
    listing = make_listing(
        id=3, venue="Arena", price=30.0, start_time=time(20, 0), end_time=time(22, 0)
    )
    alert = make_alert(id=6, venue="Arena", max_price=20.0)
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [alert]
    mock_db.execute = AsyncMock(return_value=mock_result)
    with patch(
        "app.modules.listings.router.get_parsed_listing", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = listing
        response = client.get("/parsed-listings/3/matches")
    data = response.json()
    assert data["match_count"] == 0
