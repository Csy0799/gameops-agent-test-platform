from datetime import datetime, timedelta


def activity_payload(**overrides) -> dict:
    now = datetime.utcnow()
    payload = {
        "name": "Idempotency Event",
        "start_time": (now - timedelta(days=1)).isoformat(),
        "end_time": (now + timedelta(days=1)).isoformat(),
        "reward_pool_gold": 1000,
        "reward_pool_diamond": 0,
        "drop_item_id": "item_3001",
        "drop_probability": 0.5,
        "daily_limit": 3,
        "pity_threshold": 10,
        "risk_level": "low",
    }
    payload.update(overrides)
    return payload


def create_published_activity(client, **overrides) -> dict:
    create_response = client.post("/api/activities", json=activity_payload(**overrides))
    assert create_response.status_code == 200
    activity = create_response.json()["data"]
    publish_response = client.post(f"/api/activities/{activity['id']}/publish")
    assert publish_response.status_code == 200
    return publish_response.json()["data"]


def claim_payload(activity_id: int, key: str = "idem-key") -> dict:
    return {
        "user_id": "idem_user",
        "activity_id": activity_id,
        "idempotency_key": key,
    }


def test_same_idempotency_key_does_not_issue_reward_twice(client):
    activity = create_published_activity(client)

    first = client.post("/api/rewards/claim", json=claim_payload(activity["id"]))
    second = client.post("/api/rewards/claim", json=claim_payload(activity["id"]))

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["data"]["wallet_gold"] == 100
    assert second.json()["data"]["wallet_gold"] == 100


def test_repeated_idempotency_key_returns_duplicated_true(client):
    activity = create_published_activity(client)

    client.post("/api/rewards/claim", json=claim_payload(activity["id"]))
    response = client.post("/api/rewards/claim", json=claim_payload(activity["id"]))

    assert response.status_code == 200
    assert response.json()["data"]["duplicated"] is True


def test_repeated_idempotency_key_keeps_wallet_amount_unchanged(client):
    activity = create_published_activity(client)

    client.post("/api/rewards/claim", json=claim_payload(activity["id"]))
    before = client.get("/api/users/idem_user/wallet").json()["data"]["gold"]
    client.post("/api/rewards/claim", json=claim_payload(activity["id"]))
    after = client.get("/api/users/idem_user/wallet").json()["data"]["gold"]

    assert before == 100
    assert after == 100


def test_repeated_idempotency_key_keeps_reward_pool_unchanged(client):
    activity = create_published_activity(client)

    client.post("/api/rewards/claim", json=claim_payload(activity["id"]))
    pool_after_first = client.get(f"/api/activities/{activity['id']}").json()["data"][
        "reward_pool_gold"
    ]
    client.post("/api/rewards/claim", json=claim_payload(activity["id"]))
    pool_after_second = client.get(f"/api/activities/{activity['id']}").json()["data"][
        "reward_pool_gold"
    ]

    assert pool_after_first == 900
    assert pool_after_second == 900
