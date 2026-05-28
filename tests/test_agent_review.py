import allure
import pytest

pytestmark = [
    pytest.mark.agent,
    pytest.mark.integration,
    allure.feature("Human Review"),
    allure.story("Review approval and rejection"),
]

HIGH_BUDGET_REQUIREMENT = "创建周末活动，金币预算2000000，掉率20%，每天最多领取3次"
HIGH_RATE_REQUIREMENT = "创建周末活动，金币预算1000000，掉率60%，每天最多领取3次"
DIAMOND_REQUIREMENT = "创建钻石返利活动，掉率20%，每天最多领取3次"


def create_pending_review(client, requirement=HIGH_BUDGET_REQUIREMENT):
    response = client.post("/api/agent/generate_activity", json={"requirement": requirement})
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "pending_review"
    return response.json()["data"]


def test_high_gold_budget_enters_pending_review(client):
    data = create_pending_review(client, HIGH_BUDGET_REQUIREMENT)

    assert data["reason"] == "high risk activity requires human review"


def test_high_drop_rate_enters_pending_review(client):
    data = create_pending_review(client, HIGH_RATE_REQUIREMENT)

    assert data["config"]["drop_probability"] == 0.6


def test_diamond_reward_enters_pending_review(client):
    data = create_pending_review(client, DIAMOND_REQUIREMENT)

    assert data["config"]["reward_pool_diamond"] > 0


def test_risk_level_high_enters_pending_review(client):
    data = create_pending_review(client, HIGH_BUDGET_REQUIREMENT)

    assert data["config"]["risk_level"] == "high"


def test_pending_review_returns_review_id(client):
    data = create_pending_review(client)

    assert data["review_id"].startswith("review_")


def test_approve_review_creates_draft_activity(client):
    pending = create_pending_review(client)

    response = client.post(
        f"/api/agent/review/{pending['review_id']}",
        json={"action": "approve"},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "approved"
    activity = client.get(f"/api/activities/{data['activity_id']}").json()["data"]
    assert activity["status"] == "draft"


def test_reject_review_does_not_create_activity(client):
    pending = create_pending_review(client)

    response = client.post(
        f"/api/agent/review/{pending['review_id']}",
        json={"action": "reject"},
    )

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "rejected"
    assert client.get("/api/activities").json()["data"]["total"] == 0


def test_missing_review_id_returns_not_found(client):
    response = client.post("/api/agent/review/review_missing", json={"action": "approve"})

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "not_found"


def test_invalid_review_action_returns_error(client):
    pending = create_pending_review(client)

    response = client.post(
        f"/api/agent/review/{pending['review_id']}",
        json={"action": "invalid"},
    )

    assert response.status_code == 422
    assert response.json()["code"] != 0


def test_agent_response_contains_code_message_data(client):
    response = client.post("/api/agent/generate_activity", json={"requirement": HIGH_BUDGET_REQUIREMENT})

    assert set(response.json().keys()) == {"code", "message", "data"}


def test_generate_activity_api_normal_request_success(client):
    response = client.post(
        "/api/agent/generate_activity",
        json={"requirement": "创建一个周末世界Boss活动，掉率20%，每天最多领取3次，金币预算1000000"},
    )

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "created"


def test_generate_activity_api_high_risk_returns_pending_review(client):
    response = client.post("/api/agent/generate_activity", json={"requirement": HIGH_RATE_REQUIREMENT})

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "pending_review"


def test_review_api_approve_success(client):
    pending = create_pending_review(client)

    response = client.post(
        f"/api/agent/review/{pending['review_id']}",
        json={"action": "approve"},
    )

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "approved"


def test_review_api_reject_success(client):
    pending = create_pending_review(client)

    response = client.post(
        f"/api/agent/review/{pending['review_id']}",
        json={"action": "reject"},
    )

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "rejected"
