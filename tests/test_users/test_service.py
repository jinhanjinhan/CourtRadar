from unittest.mock import AsyncMock, patch

import pytest

from app.modules.users.schemas import UserCreate
from app.modules.users.service import create_user, get_user
from tests.factories import make_user


async def test_create_user_success():
    user = make_user()
    session = AsyncMock()
    with (
        patch("app.modules.users.service.repository.get_user_by_email", new_callable=AsyncMock) as mock_get,
        patch("app.modules.users.service.repository.create_user", new_callable=AsyncMock) as mock_create,
    ):
        mock_get.return_value = None
        mock_create.return_value = user
        result = await create_user(session, UserCreate(email="test@example.com", display_name="Test User"))
    assert result == user
    mock_create.assert_called_once()


async def test_create_user_email_already_exists_raises():
    session = AsyncMock()
    existing = make_user()
    with patch("app.modules.users.service.repository.get_user_by_email", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = existing
        with pytest.raises(ValueError, match="email already exists"):
            await create_user(session, UserCreate(email="test@example.com", display_name="Test User"))


async def test_create_user_with_telegram_chat_id():
    user = make_user(telegram_chat_id="123456789")
    session = AsyncMock()
    with (
        patch("app.modules.users.service.repository.get_user_by_email", new_callable=AsyncMock) as mock_get,
        patch("app.modules.users.service.repository.create_user", new_callable=AsyncMock) as mock_create,
    ):
        mock_get.return_value = None
        mock_create.return_value = user
        result = await create_user(
            session,
            UserCreate(email="test@example.com", display_name="Test", telegram_chat_id="123456789"),
        )
    assert result.telegram_chat_id == "123456789"


async def test_get_user_found():
    user = make_user(id=5)
    session = AsyncMock()
    with patch("app.modules.users.service.repository.get_user_by_id", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = user
        result = await get_user(session, 5)
    assert result == user
    mock_get.assert_called_once_with(session, 5)


async def test_get_user_not_found_returns_none():
    session = AsyncMock()
    with patch("app.modules.users.service.repository.get_user_by_id", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        result = await get_user(session, 999)
    assert result is None
