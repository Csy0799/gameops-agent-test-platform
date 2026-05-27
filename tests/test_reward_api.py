from datetime import datetime, timedelta


def activity_payload(**overrides) -> dict:
    now = datetime.utcnow()
    payload = {
        "name": "Reward Claim Event",
        "start_time": (now - timedelta(days=1)).isoformat(),
        "end_time": (now + timedelta(days=1)).isoformat(),
        "reward_pool_gold": 1000,
        "reward_pool_diamond": 0,
        "drop_item_id": "item_2001",
        "drop_probability": 0.5,
        "daily_limit": 3,
        "pity_threshold": 10,
        "risk_level": "low",
    }
    payload.update(overrides)
    return payload


def create_activity(client, **overrides) -> dict:
    response = client.post("/api/activities", json=activity_payload(**overrides))
    assert response.status_code == 200
    return response.json()["data"]


def create_published_activity(client, **overrides) -> dict:
    activity = create_activity(client, **overrides)
    response = client.post(f"/api/activities/{activity['id']}/publish")
    assert response.status_code == 200
    return response.json()["data"]


def claim_payload(activity_id: int, user_id: str = "user_001", key: str = "claim-001"):
    return {
        "user_id": user_id,
        "activity_id": activity_id,
        "idempotency_key": key,
    }


def claim_reward(client, activity_id: int, user_id: str = "user_001", key: str = "claim-001"):
    response = client.post(
        "/api/rewards/claim",
        json=claim_payload(activity_id, user_id=user_id, key=key),
    )
    assert response.status_code == 200
    return response.json()["data"]


def test_claim_published_activity_success(client):
    activity = create_published_activity(client)

    data = claim_reward(client, activity["id"])

    assert data["reward_gold"] == 100
    assert data["duplicated"] is False


def test_wallet_gold_increases_after_successful_claim(client):
    activity = create_published_activity(client)

    claim_reward(client, activity["id"])
    response = client.get("/api/users/user_001/wallet")

    assert response.status_code == 200
    assert response.json()["data"]["gold"] == 100


def test_activity_reward_pool_gold_decreases_after_successful_claim(client):
    activity = create_published_activity(client, reward_pool_gold=1000)

    claim_reward(client, activity["id"])
    response = client.get(f"/api/activities/{activity['id']}")

    assert response.status_code == 200
    assert response.json()["data"]["reward_pool_gold"] == 900


def test_reward_record_created_after_successful_claim(client):
    activity = create_published_activity(client)

    claim_reward(client, activity["id"], key="record-key")
    response = client.get("/api/rewards/records")

    assert response.status_code == 200
    records = response.json()["data"]
    assert len(records) == 1
    assert records[0]["idempotency_key"] == "record-key"
    assert records[0]["status"] == "success"


def test_get_existing_user_wallet_success(client):
    activity = create_published_activity(client)
    claim_reward(client, activity["id"], user_id="wallet_user")

    response = client.get("/api/users/wallet_user/wallet")

    assert response.status_code == 200
    assert response.json()["data"] == {
        "user_id": "wallet_user",
        "gold": 100,
        "diamond": 0,
    }


def test_get_missing_user_wallet_returns_zero_wallet(client):
    response = client.get("/api/users/new_user/wallet")

    assert response.status_code == 200
    assert response.json()["data"] == {
        "user_id": "new_user",
        "gold": 0,
        "diamond": 0,
    }


def test_draft_activity_cannot_be_claimed(client):
    activity = create_activity(client)

    response = client.post("/api/rewards/claim", json=claim_payload(activity["id"]))

    assert response.status_code == 400
    assert response.json()["message"] == "only published activity can be claimed"


def test_rolled_back_activity_cannot_be_claimed(client):
    activity = create_published_activity(client)
    rollback_response = client.post(f"/api/activities/{activity['id']}/rollback")
    assert rollback_response.status_code == 200

    response = client.post("/api/rewards/claim", json=claim_payload(activity["id"]))

    assert response.status_code == 400
    assert response.json()["message"] == "only published activity can be claimed"


def test_missing_activity_cannot_be_claimed(client):
    response = client.post("/api/rewards/claim", json=claim_payload(999))

    assert response.status_code == 404
    assert response.json()["message"] == "activity not found"


def test_not_started_activity_cannot_be_claimed(client):
    now = datetime.utcnow()
    activity = create_published_activity(
        client,
        start_time=(now + timedelta(days=1)).isoformat(),
        end_time=(now + timedelta(days=2)).isoformat(),
    )

    response = client.post("/api/rewards/claim", json=claim_payload(activity["id"]))

    assert response.status_code == 400
    assert response.json()["message"] == "activity has not started"


def test_ended_activity_cannot_be_claimed(client):
    now = datetime.utcnow()
    activity = create_published_activity(
        client,
        start_time=(now - timedelta(days=2)).isoformat(),
        end_time=(now - timedelta(days=1)).isoformat(),
    )

    response = client.post("/api/rewards/claim", json=claim_payload(activity["id"]))

    assert response.status_code == 400
    assert response.json()["message"] == "activity has ended"


def test_insufficient_reward_pool_cannot_be_claimed(client):
    activity = create_published_activity(client, reward_pool_gold=50)

    response = client.post("/api/rewards/claim", json=claim_payload(activity["id"]))

    assert response.status_code == 400
    assert response.json()["message"] == "reward gold pool is insufficient"


def test_daily_limit_one_blocks_second_distinct_claim(client):
    activity = create_published_activity(client, daily_limit=1, reward_pool_gold=1000)
    claim_reward(client, activity["id"], key="daily-key-1")

    response = client.post(
        "/api/rewards/claim",
        json=claim_payload(activity["id"], key="daily-key-2"),
    )

    assert response.status_code == 400
    assert response.json()["message"] == "daily claim limit exceeded"


def test_different_idempotency_keys_can_claim_until_daily_limit(client):
    activity = create_published_activity(client, daily_limit=2, reward_pool_gold=1000)

    first = claim_reward(client, activity["id"], key="multi-key-1")
    second = claim_reward(client, activity["id"], key="multi-key-2")

    assert first["wallet_gold"] == 100
    assert second["wallet_gold"] == 200


def test_missing_user_id_returns_validation_error(client):
    activity = create_published_activity(client)
    payload = claim_payload(activity["id"])
    payload.pop("user_id")

    response = client.post("/api/rewards/claim", json=payload)

    assert response.status_code == 422
    assert response.json()["code"] != 0


def test_missing_idempotency_key_returns_validation_error(client):
    activity = create_published_activity(client)
    payload = claim_payload(activity["id"])
    payload.pop("idempotency_key")

    response = client.post("/api/rewards/claim", json=payload)

    assert response.status_code == 422
    assert response.json()["code"] != 0


def test_list_reward_records_success(client):
    activity = create_published_activity(client)
    claim_reward(client, activity["id"], key="list-key")

    response = client.get("/api/rewards/records")

    assert response.status_code == 200
    assert response.json()["data"][0]["idempotency_key"] == "list-key"


def test_reward_response_contains_code_message_data(client):
    activity = create_published_activity(client)

    response = client.post("/api/rewards/claim", json=claim_payload(activity["id"]))

    body = response.json()
    assert set(body.keys()) == {"code", "message", "data"}
    assert body["code"] == 0
    assert body["message"] == "success"
    assert isinstance(body["data"], dict)


def test_claim_response_contains_reward_wallet_and_idempotency_fields(client):
    activity = create_published_activity(client)

    data = claim_reward(client, activity["id"], key="field-key")

    assert data["reward_gold"] == 100
    assert data["wallet_gold"] == 100
    assert data["idempotency_key"] == "field-key"
