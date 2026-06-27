from datetime import time
from unittest.mock import AsyncMock, patch

import pytest

from app.modules.alerts.schemas import AlertPreferenceCreate
from app.modules.alerts.service import create_alert_preference, list_alert_preferences
from tests.factories import make_alert, make_user


async def test_create_alert_preference_success():
    session = AsyncMock()
    user = make_user()
    session.get.return_value = user
    alert = make_alert()
    with patch("app.modules.alerts.service.repository.create_alert_preference", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = alert
        result = await create_alert_preference(
            session,
            AlertPreferenceCreate(user_id=1, venue="Test Venue", max_price=20.0),
        )
    assert result == alert
    mock_create.assert_called_once()


async def test_create_alert_preference_user_not_found_raises():
    session = AsyncMock()
    session.get.return_value = None
    with pytest.raises(ValueError, match="user not found"):
        await create_alert_preference(
            session,
            AlertPreferenceCreate(user_id=999),
        )


async def test_create_alert_preference_with_time_constraints():
    session = AsyncMock()
    session.get.return_value = make_user()
    alert = make_alert(earliest_time=time(8, 0), latest_time=time(22, 0))
    with patch("app.modules.alerts.service.repository.create_alert_preference", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = alert
        result = await create_alert_preference(
            session,
            AlertPreferenceCreate(user_id=1, earliest_time=time(8, 0), latest_time=time(22, 0)),
        )
    assert result.earliest_time == time(8, 0)
    assert result.latest_time == time(22, 0)


async def test_list_alert_preferences_all():
    session = AsyncMock()
    alerts = [make_alert(id=1), make_alert(id=2)]
    with patch(
        "app.modules.alerts.service.repository.list_alert_preferences", new_callable=AsyncMock
    ) as mock_list:
        mock_list.return_value = alerts
        result = await list_alert_preferences(session)
    assert result == alerts
    mock_list.assert_called_once_with(session, user_id=None)


async def test_list_alert_preferences_filtered_by_user():
    session = AsyncMock()
    alerts = [make_alert(id=1, user_id=42)]
    with patch(
        "app.modules.alerts.service.repository.list_alert_preferences", new_callable=AsyncMock
    ) as mock_list:
        mock_list.return_value = alerts
        result = await list_alert_preferences(session, user_id=42)
    assert result == alerts
    mock_list.assert_called_once_with(session, user_id=42)


async def test_list_alert_preferences_empty():
    session = AsyncMock()
    with patch(
        "app.modules.alerts.service.repository.list_alert_preferences", new_callable=AsyncMock
    ) as mock_list:
        mock_list.return_value = []
        result = await list_alert_preferences(session)
    assert result == []
