from datetime import time
from unittest.mock import AsyncMock, patch


from tests.factories import make_alert


def test_create_alert_preference_success(client):
    alert = make_alert(id=3, user_id=1, venue="Arena", max_price=25.0)
    with patch(
        "app.modules.alerts.router.create_alert_preference", new_callable=AsyncMock
    ) as mock:
        mock.return_value = alert
        response = client.post(
            "/alert-preferences",
            json={"user_id": 1, "venue": "Arena", "max_price": 25.0},
        )
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 3
    assert "created_at" in data


def test_create_alert_preference_user_not_found_returns_404(client):
    with patch(
        "app.modules.alerts.router.create_alert_preference", new_callable=AsyncMock
    ) as mock:
        mock.side_effect = ValueError("user not found")
        response = client.post("/alert-preferences", json={"user_id": 999})
    assert response.status_code == 404
    assert response.json()["detail"] == "user not found"


def test_create_alert_preference_minimal_payload(client):
    alert = make_alert(user_id=2)
    with patch(
        "app.modules.alerts.router.create_alert_preference", new_callable=AsyncMock
    ) as mock:
        mock.return_value = alert
        response = client.post("/alert-preferences", json={"user_id": 2})
    assert response.status_code == 201


def test_create_alert_preference_with_time_constraints(client):
    alert = make_alert(earliest_time=time(8, 0), latest_time=time(22, 0))
    with patch(
        "app.modules.alerts.router.create_alert_preference", new_callable=AsyncMock
    ) as mock:
        mock.return_value = alert
        response = client.post(
            "/alert-preferences",
            json={"user_id": 1, "earliest_time": "08:00:00", "latest_time": "22:00:00"},
        )
    assert response.status_code == 201


def test_create_alert_preference_missing_user_id_returns_422(client):
    response = client.post("/alert-preferences", json={"venue": "Arena"})
    assert response.status_code == 422


def test_list_alert_preferences_returns_all(client):
    alerts = [make_alert(id=1, user_id=1), make_alert(id=2, user_id=2)]
    with patch(
        "app.modules.alerts.router.list_alert_preferences", new_callable=AsyncMock
    ) as mock:
        mock.return_value = alerts
        response = client.get("/alert-preferences")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["id"] == 1
    assert data[1]["id"] == 2


def test_list_alert_preferences_filtered_by_user_id(client):
    alerts = [make_alert(id=1, user_id=5)]
    with patch(
        "app.modules.alerts.router.list_alert_preferences", new_callable=AsyncMock
    ) as mock:
        mock.return_value = alerts
        response = client.get("/alert-preferences?user_id=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["user_id"] == 5


def test_list_alert_preferences_empty(client):
    with patch(
        "app.modules.alerts.router.list_alert_preferences", new_callable=AsyncMock
    ) as mock:
        mock.return_value = []
        response = client.get("/alert-preferences")
    assert response.status_code == 200
    assert response.json() == []


def test_list_alert_preferences_includes_is_active_field(client):
    alert = make_alert(is_active=True)
    with patch(
        "app.modules.alerts.router.list_alert_preferences", new_callable=AsyncMock
    ) as mock:
        mock.return_value = [alert]
        response = client.get("/alert-preferences")
    data = response.json()
    assert data[0]["is_active"] is True
