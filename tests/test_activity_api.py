import allure
import pytest
from copy import deepcopy

pytestmark = [
    pytest.mark.api,
    pytest.mark.regression,
    allure.feature("Activity Management"),
    allure.story("Activity API"),
]


def activity_payload() -> dict:
    return {
        "name": "Spring Festival Login Event",
        "start_time": "2026-06-01T00:00:00",
        "end_time": "2026-06-10T23:59:59",
        "reward_pool_gold": 10000,
        "reward_pool_diamond": 500,
        "drop_item_id": "item_1001",
        "drop_probability": 0.25,
        "daily_limit": 3,
        "pity_threshold": 10,
        "risk_level": "low",
    }


def create_activity(client, payload=None) -> dict:
    response = client.post("/api/activities", json=payload or activity_payload())
    assert response.status_code == 200
    return response.json()["data"]


def test_create_valid_activity_success(client):
    response = client.post("/api/activities", json=activity_payload())

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 0
    assert body["message"] == "success"
    assert body["data"]["name"] == "Spring Festival Login Event"


def test_create_activity_default_status_is_draft(client):
    data = create_activity(client)

    assert data["status"] == "draft"


def test_create_activity_with_probability_less_than_zero_fails(client):
    payload = activity_payload()
    payload["drop_probability"] = -0.01

    response = client.post("/api/activities", json=payload)

    assert response.status_code == 422
    assert response.json()["code"] != 0


def test_create_activity_with_probability_greater_than_one_fails(client):
    payload = activity_payload()
    payload["drop_probability"] = 1.01

    response = client.post("/api/activities", json=payload)

    assert response.status_code == 422
    assert response.json()["code"] != 0


def test_create_activity_with_probability_zero_success(client):
    payload = activity_payload()
    payload["drop_probability"] = 0

    data = create_activity(client, payload)

    assert data["drop_probability"] == 0


def test_create_activity_with_probability_one_success(client):
    payload = activity_payload()
    payload["drop_probability"] = 1

    data = create_activity(client, payload)

    assert data["drop_probability"] == 1


def test_create_activity_with_invalid_time_range_fails(client):
    payload = activity_payload()
    payload["start_time"] = payload["end_time"]

    response = client.post("/api/activities", json=payload)

    assert response.status_code == 422
    assert response.json()["code"] != 0


def test_create_activity_with_daily_limit_not_positive_fails(client):
    payload = activity_payload()
    payload["daily_limit"] = 0

    response = client.post("/api/activities", json=payload)

    assert response.status_code == 422
    assert response.json()["code"] != 0


def test_create_activity_with_negative_gold_pool_fails(client):
    payload = activity_payload()
    payload["reward_pool_gold"] = -1

    response = client.post("/api/activities", json=payload)

    assert response.status_code == 422
    assert response.json()["code"] != 0


def test_create_activity_with_negative_diamond_pool_fails(client):
    payload = activity_payload()
    payload["reward_pool_diamond"] = -1

    response = client.post("/api/activities", json=payload)

    assert response.status_code == 422
    assert response.json()["code"] != 0


def test_get_existing_activity_success(client):
    created = create_activity(client)

    response = client.get(f"/api/activities/{created['id']}")

    assert response.status_code == 200
    assert response.json()["data"]["id"] == created["id"]


def test_get_missing_activity_fails(client):
    response = client.get("/api/activities/999")

    assert response.status_code == 404
    assert response.json() == {
        "code": 404,
        "message": "activity not found",
        "data": None,
    }


def test_list_activities_success(client):
    first_payload = activity_payload()
    second_payload = deepcopy(first_payload)
    second_payload["name"] = "Weekend Drop Event"
    create_activity(client, first_payload)
    create_activity(client, second_payload)

    response = client.get("/api/activities")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total"] == 2
    assert [item["name"] for item in data["items"]] == [
        "Spring Festival Login Event",
        "Weekend Drop Event",
    ]


def test_publish_draft_activity_success(client):
    created = create_activity(client)

    response = client.post(f"/api/activities/{created['id']}/publish")

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "published"


def test_publish_activity_twice_fails(client):
    created = create_activity(client)
    client.post(f"/api/activities/{created['id']}/publish")

    response = client.post(f"/api/activities/{created['id']}/publish")

    assert response.status_code == 400
    assert response.json()["message"] == "activity already published"


def test_rollback_published_activity_success(client):
    created = create_activity(client)
    client.post(f"/api/activities/{created['id']}/publish")

    response = client.post(f"/api/activities/{created['id']}/rollback")

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "rolled_back"


def test_rollback_draft_activity_fails(client):
    created = create_activity(client)

    response = client.post(f"/api/activities/{created['id']}/rollback")

    assert response.status_code == 400
    assert response.json()["message"] == "only published activity can be rolled back"


def test_activity_response_contains_code_message_data(client):
    response = client.post("/api/activities", json=activity_payload())

    body = response.json()
    assert set(body.keys()) == {"code", "message", "data"}
    assert body["code"] == 0
    assert body["message"] == "success"
    assert isinstance(body["data"], dict)
