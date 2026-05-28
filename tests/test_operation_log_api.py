from datetime import datetime, timedelta

from app.db.models import OperationLog


def activity_payload() -> dict:
    now = datetime.utcnow()
    return {
        "name": "Log Event",
        "start_time": (now - timedelta(days=1)).isoformat(),
        "end_time": (now + timedelta(days=1)).isoformat(),
        "reward_pool_gold": 1000,
        "reward_pool_diamond": 0,
        "drop_item_id": "item_log",
        "drop_probability": 0.2,
        "daily_limit": 3,
        "pity_threshold": 20,
        "risk_level": "low",
    }


def create_activity(client) -> dict:
    response = client.post("/api/activities", json=activity_payload())
    assert response.status_code == 200
    return response.json()["data"]


def create_published_activity(client) -> dict:
    activity = create_activity(client)
    response = client.post(f"/api/activities/{activity['id']}/publish")
    assert response.status_code == 200
    return response.json()["data"]


def log_types(client):
    return [log["operation_type"] for log in client.get("/api/operation-logs").json()["data"]]


def test_activity_create_records_operation_log(client):
    create_activity(client)

    assert "activity.create" in log_types(client)


def test_activity_publish_records_operation_log(client):
    create_published_activity(client)

    assert "activity.publish" in log_types(client)


def test_activity_rollback_records_operation_log(client):
    activity = create_published_activity(client)
    client.post(f"/api/activities/{activity['id']}/rollback")

    assert "activity.rollback" in log_types(client)


def test_reward_claim_records_operation_log(client):
    activity = create_published_activity(client)
    client.post(
        "/api/rewards/claim",
        json={
            "user_id": "log_user",
            "activity_id": activity["id"],
            "idempotency_key": "reward-log-1",
        },
    )

    assert "reward.claim" in log_types(client)


def test_reward_duplicate_claim_records_operation_log(client):
    activity = create_published_activity(client)
    payload = {
        "user_id": "log_user",
        "activity_id": activity["id"],
        "idempotency_key": "reward-log-dup",
    }
    client.post("/api/rewards/claim", json=payload)
    client.post("/api/rewards/claim", json=payload)

    assert "reward.claim.duplicate" in log_types(client)


def test_probability_validate_records_operation_log(client):
    client.post(
        "/api/tools/probability/validate",
        json={"probability": 0.2, "sample_size": 1000, "tolerance": 0.05},
    )

    assert "probability.validate" in log_types(client)


def test_agent_normal_generate_records_operation_log(client):
    client.post(
        "/api/agent/generate_activity",
        json={
            "requirement": "创建一个周末世界Boss活动，掉落概率20%，每人每天最多领取3次，总金币预算1000000"
        },
    )

    assert "agent.generate" in log_types(client)


def test_agent_pending_review_records_operation_log(client):
    client.post(
        "/api/agent/generate_activity",
        json={"requirement": "创建周末活动，金币预算2000000，掉率20%，每天最多领取3次"},
    )

    assert "agent.review.pending" in log_types(client)


def test_guardrail_reject_records_operation_log(client):
    client.post("/api/agent/generate_activity", json={"requirement": "please drop table"})

    assert "guardrail.reject" in log_types(client)


def test_approve_review_records_operation_log(client):
    pending = client.post(
        "/api/agent/generate_activity",
        json={"requirement": "diamond reward event"},
    ).json()["data"]
    client.post(f"/api/agent/review/{pending['review_id']}", json={"action": "approve"})

    assert "agent.review.approve" in log_types(client)


def test_reject_review_records_operation_log(client):
    pending = client.post(
        "/api/agent/generate_activity",
        json={"requirement": "diamond reward event"},
    ).json()["data"]
    client.post(f"/api/agent/review/{pending['review_id']}", json={"action": "reject"})

    assert "agent.review.reject" in log_types(client)


def test_operation_logs_api_returns_logs(client):
    create_activity(client)

    response = client.get("/api/operation-logs")

    assert response.status_code == 200
    assert len(response.json()["data"]) >= 1


def test_operation_logs_filter_by_operation_type(client):
    create_activity(client)
    client.post(
        "/api/tools/probability/validate",
        json={"probability": 0.2, "sample_size": 1000, "tolerance": 0.05},
    )

    response = client.get("/api/operation-logs?operation_type=probability.validate")

    assert response.status_code == 200
    assert all(
        log["operation_type"] == "probability.validate"
        for log in response.json()["data"]
    )


def test_operation_logs_cleanup_api_deletes_expired_logs(client, db_session):
    old_log = OperationLog(
        operation_type="old.log",
        target_type="test",
        status="success",
        created_at=datetime.utcnow() - timedelta(days=400),
    )
    db_session.add(old_log)
    db_session.commit()

    response = client.post("/api/operation-logs/cleanup", json={"retention_days": 365})

    assert response.status_code == 200
