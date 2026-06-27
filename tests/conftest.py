from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.deps import db_session
from app.main import create_app


@pytest.fixture
def mock_db():
    session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_result.scalar_one_or_none.return_value = None
    session.execute.return_value = mock_result
    session.get.return_value = None
    return session


@pytest.fixture
def client(mock_db):
    app = create_app()

    async def override_db_session():
        yield mock_db

    app.dependency_overrides[db_session] = override_db_session
    with TestClient(app) as c:
        yield c
