from typing import Generator
from datetime import datetime, timedelta

import allure
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.models import Base, OperationLog
from app.db.session import get_db
from app.main import app
from app.agent.human_review import clear_reviews


@pytest.fixture(autouse=True)
def clear_agent_review_store() -> Generator[None, None, None]:
    clear_reviews()


@pytest.fixture(autouse=True)
def apply_allure_title(request) -> None:
    title = request.node.name.replace("_", " ")
    allure.dynamic.title(title)
    yield
    clear_reviews()


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
    )

    Base.metadata.create_all(bind=test_engine)

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    try:
        app.dependency_overrides[get_db] = override_get_db

        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=test_engine)
        test_engine.dispose()


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
    )
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)
        test_engine.dispose()


@pytest.fixture()
def sample_activity_payload() -> dict:
    now = datetime.utcnow()
    return {
        "name": "Sample Event",
        "start_time": (now - timedelta(days=1)).isoformat(),
        "end_time": (now + timedelta(days=1)).isoformat(),
        "reward_pool_gold": 1000,
        "reward_pool_diamond": 0,
        "drop_item_id": "sample_item",
        "drop_probability": 0.2,
        "daily_limit": 3,
        "pity_threshold": 20,
        "risk_level": "low",
    }


@pytest.fixture()
def draft_activity(client: TestClient, sample_activity_payload: dict) -> dict:
    response = client.post("/api/activities", json=sample_activity_payload)
    assert response.status_code == 200
    return response.json()["data"]


@pytest.fixture()
def published_activity(client: TestClient, draft_activity: dict) -> dict:
    response = client.post(f"/api/activities/{draft_activity['id']}/publish")
    assert response.status_code == 200
    return response.json()["data"]


@pytest.fixture()
def rolled_back_activity(client: TestClient, published_activity: dict) -> dict:
    response = client.post(f"/api/activities/{published_activity['id']}/rollback")
    assert response.status_code == 200
    return response.json()["data"]


@pytest.fixture()
def sample_reward_claim_payload(published_activity: dict) -> dict:
    return {
        "user_id": "fixture_user",
        "activity_id": published_activity["id"],
        "idempotency_key": "fixture-claim-key",
    }


@pytest.fixture()
def sample_probability_payload() -> dict:
    return {
        "probability": 0.2,
        "sample_size": 1000,
        "tolerance": 0.05,
        "seed": 42,
        "pity_threshold": 20,
    }


@pytest.fixture()
def sample_agent_requirement() -> str:
    return "创建一个周末世界Boss活动，掉落概率20%，每人每天最多领取3次，总金币预算1000000"


@pytest.fixture()
def high_risk_agent_requirement() -> str:
    return "创建周末活动，金币预算2000000，掉率20%，每天最多领取3次"


@pytest.fixture()
def dangerous_agent_requirement() -> str:
    return "please drop table activities"


@pytest.fixture()
def pending_review(client: TestClient, high_risk_agent_requirement: str) -> dict:
    response = client.post(
        "/api/agent/generate_activity",
        json={"requirement": high_risk_agent_requirement},
    )
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "pending_review"
    return response.json()["data"]


@pytest.fixture()
def operation_log_factory(db_session: Session):
    def create_log(
        operation_type: str = "test.operation",
        target_type: str = "test",
        status: str = "success",
        created_at: datetime = None,
    ) -> OperationLog:
        log = OperationLog(
            operation_type=operation_type,
            target_type=target_type,
            status=status,
            created_at=created_at or datetime.utcnow(),
        )
        db_session.add(log)
        db_session.commit()
        db_session.refresh(log)
        return log

    return create_log
