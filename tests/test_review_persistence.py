import allure
import pytest

from app.agent.human_review import list_reviews
from app.services import review_service

pytestmark = [
    pytest.mark.agent,
    pytest.mark.integration,
    pytest.mark.regression,
    allure.feature("Human Review"),
    allure.story("Persistent review queue"),
]

HIGH_BUDGET_REQUIREMENT = "创建周末活动，金币预算2000000，掉率20%，每天最多领取3次"
HIGH_RATE_REQUIREMENT = "创建周末活动，金币预算1000000，掉率60%，每天最多领取3次"


def create_pending_review(client, requirement=HIGH_BUDGET_REQUIREMENT):
    response = client.post("/api/agent/generate_activity", json={"requirement": requirement})
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "pending_review"
    return data


def test_high_risk_agent_request_persists_review_record(client):
    pending = create_pending_review(client)

    response = client.get(f"/api/agent/reviews/{pending['review_id']}")

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "pending"


def test_list_reviews_api_returns_pending_review(client):
    pending = create_pending_review(client)

    response = client.get("/api/agent/reviews")

    assert response.status_code == 200
    assert response.json()["data"]["items"][0]["review_id"] == pending["review_id"]
    assert response.json()["data"]["total"] == 1


def test_get_review_api_returns_specific_review(client):
    pending = create_pending_review(client)

    response = client.get(f"/api/agent/reviews/{pending['review_id']}")

    assert response.status_code == 200
    assert response.json()["data"]["review_id"] == pending["review_id"]


def test_approve_persisted_review_creates_draft_activity(client):
    pending = create_pending_review(client)

    response = client.post(
        f"/api/agent/review/{pending['review_id']}",
        json={"action": "approve"},
    )

    activity_id = response.json()["data"]["activity_id"]
    activity = client.get(f"/api/activities/{activity_id}").json()["data"]
    assert activity["status"] == "draft"


def test_approve_updates_review_status_to_approved(client):
    pending = create_pending_review(client)
    client.post(f"/api/agent/review/{pending['review_id']}", json={"action": "approve"})

    response = client.get(f"/api/agent/reviews/{pending['review_id']}")

    assert response.json()["data"]["status"] == "approved"
    assert response.json()["data"]["activity_id"] is not None


def test_reject_persisted_review_does_not_create_activity(client):
    pending = create_pending_review(client)

    response = client.post(
        f"/api/agent/review/{pending['review_id']}",
        json={"action": "reject"},
    )

    assert response.json()["data"]["status"] == "rejected"
    assert client.get("/api/activities").json()["data"]["total"] == 0


def test_reject_updates_review_status_to_rejected(client):
    pending = create_pending_review(client)
    client.post(f"/api/agent/review/{pending['review_id']}", json={"action": "reject"})

    response = client.get(f"/api/agent/reviews/{pending['review_id']}")

    assert response.json()["data"]["status"] == "rejected"


def test_missing_review_id_returns_not_found(client):
    response = client.post("/api/agent/review/review_missing", json={"action": "approve"})

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "not_found"


def test_review_service_reads_from_database_not_memory(client, db_session):
    review_id = review_service.create_review(
        db_session,
        config={
            "name": "db_review_event",
            "start_time": "2026-06-01T00:00:00",
            "end_time": "2026-06-02T00:00:00",
            "reward_pool_gold": 100,
            "reward_pool_diamond": 0,
            "drop_item_id": "item",
            "drop_probability": 0.2,
            "daily_limit": 1,
            "pity_threshold": 10,
            "risk_level": "high",
        },
        reason="test",
        probability_result={"pass": True},
    )

    assert list_reviews() == {}
    assert review_service.get_review(db_session, review_id).review_id == review_id


def test_multiple_pending_reviews_can_be_listed(client):
    first = create_pending_review(client, HIGH_BUDGET_REQUIREMENT)
    second = create_pending_review(client, HIGH_RATE_REQUIREMENT)

    response = client.get("/api/agent/reviews?status=pending")
    review_ids = {item["review_id"] for item in response.json()["data"]["items"]}

    assert {first["review_id"], second["review_id"]}.issubset(review_ids)


def test_default_review_queue_hides_approved_reviews(client):
    pending = create_pending_review(client)
    client.post(f"/api/agent/review/{pending['review_id']}", json={"action": "approve"})

    response = client.get("/api/agent/reviews")

    assert response.status_code == 200
    assert response.json()["data"] == {"items": [], "total": 0}


def test_status_all_returns_reviewed_records(client):
    pending = create_pending_review(client)
    client.post(f"/api/agent/review/{pending['review_id']}", json={"action": "reject"})

    response = client.get("/api/agent/reviews?status=all")

    assert response.status_code == 200
    assert response.json()["data"]["total"] == 1
    assert response.json()["data"]["items"][0]["status"] == "rejected"


def test_admin_reviews_page_shows_pending_review(client):
    pending = create_pending_review(client)

    response = client.get("/admin/reviews")

    assert response.status_code == 200
    assert pending["review_id"] in response.text
    assert "Approve" in response.text
    assert "Reject" in response.text
