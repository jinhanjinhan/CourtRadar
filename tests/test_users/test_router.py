from unittest.mock import AsyncMock, patch


from tests.factories import make_user


def test_create_user_success(client):
    user = make_user(id=1, email="new@example.com", display_name="New User")
    with patch("app.modules.users.router.create_user", new_callable=AsyncMock) as mock:
        mock.return_value = user
        response = client.post("/users", json={"email": "new@example.com", "display_name": "New User"})
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert "created_at" in data


def test_create_user_duplicate_email_returns_409(client):
    with patch("app.modules.users.router.create_user", new_callable=AsyncMock) as mock:
        mock.side_effect = ValueError("email already exists")
        response = client.post("/users", json={"email": "dup@example.com", "display_name": "User"})
    assert response.status_code == 409
    assert response.json()["detail"] == "email already exists"


def test_create_user_other_value_error_returns_400(client):
    with patch("app.modules.users.router.create_user", new_callable=AsyncMock) as mock:
        mock.side_effect = ValueError("some other error")
        response = client.post("/users", json={"email": "x@example.com", "display_name": "User"})
    assert response.status_code == 400
    assert response.json()["detail"] == "some other error"


def test_create_user_missing_required_fields_returns_422(client):
    response = client.post("/users", json={"email": "test@example.com"})
    assert response.status_code == 422


def test_create_user_with_telegram_chat_id(client):
    user = make_user(telegram_chat_id="987654321")
    with patch("app.modules.users.router.create_user", new_callable=AsyncMock) as mock:
        mock.return_value = user
        response = client.post(
            "/users",
            json={"email": "tg@example.com", "display_name": "TG User", "telegram_chat_id": "987654321"},
        )
    assert response.status_code == 201


def test_get_user_success(client):
    user = make_user(id=7, email="found@example.com", display_name="Found User")
    with patch("app.modules.users.router.get_user", new_callable=AsyncMock) as mock:
        mock.return_value = user
        response = client.get("/users/7")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 7
    assert data["email"] == "found@example.com"
    assert data["display_name"] == "Found User"


def test_get_user_not_found_returns_404(client):
    with patch("app.modules.users.router.get_user", new_callable=AsyncMock) as mock:
        mock.return_value = None
        response = client.get("/users/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "user not found"


def test_get_user_with_telegram_chat_id(client):
    user = make_user(telegram_chat_id="12345")
    with patch("app.modules.users.router.get_user", new_callable=AsyncMock) as mock:
        mock.return_value = user
        response = client.get("/users/1")
    assert response.status_code == 200
    assert response.json()["telegram_chat_id"] == "12345"


def test_get_user_without_telegram_chat_id(client):
    user = make_user(telegram_chat_id=None)
    with patch("app.modules.users.router.get_user", new_callable=AsyncMock) as mock:
        mock.return_value = user
        response = client.get("/users/1")
    assert response.status_code == 200
    assert response.json()["telegram_chat_id"] is None
