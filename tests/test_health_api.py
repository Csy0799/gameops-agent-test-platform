import allure
import pytest
from fastapi.testclient import TestClient

from app.main import app

pytestmark = [
    pytest.mark.api,
    pytest.mark.regression,
    allure.feature("Health Check"),
    allure.story("Health API"),
]


@allure.title("Health API returns success response")
def test_health_api_returns_ok() -> None:
    client = TestClient(app)

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "code": 0,
        "message": "success",
        "data": {
            "status": "ok",
        },
    }
