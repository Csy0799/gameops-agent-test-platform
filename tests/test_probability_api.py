def test_probability_validate_api_returns_unified_response(client):
    response = client.post(
        "/api/tools/probability/validate",
        json={"probability": 0.2, "sample_size": 1000, "tolerance": 0.05},
    )

    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"code", "message", "data"}
    assert body["code"] == 0
    assert body["message"] == "success"


def test_probability_validate_api_invalid_probability_returns_error(client):
    response = client.post(
        "/api/tools/probability/validate",
        json={"probability": 1.1},
    )

    assert response.status_code == 400
    assert response.json() == {
        "code": 400,
        "message": "probability must be between 0 and 1",
        "data": None,
    }


def test_probability_validate_api_response_contains_simulation_fields(client):
    response = client.post(
        "/api/tools/probability/validate",
        json={"probability": 0.2, "sample_size": 1000, "tolerance": 0.05},
    )

    data = response.json()["data"]
    assert "expected_probability" in data
    assert "actual_probability" in data
    assert "deviation" in data
    assert "pass" in data
    assert "warnings" in data


def test_probability_validate_api_low_probability_warning(client):
    response = client.post(
        "/api/tools/probability/validate",
        json={"probability": 0.005, "sample_size": 1000, "tolerance": 0.05},
    )

    assert response.status_code == 200
    assert response.json()["data"]["warnings"] == [
        "low probability without pity threshold should be reviewed"
    ]
