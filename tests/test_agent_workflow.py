from app.agent.graph import AgentWorkflow
from app.agent.human_review import list_reviews
from app.agent.fake_llm import FakeLLMProvider


NORMAL_REQUIREMENT = "创建一个周末世界Boss活动，掉落概率20%，每人每天最多领取3次，总金币预算1000000"


def test_agent_normal_requirement_generate_success(client):
    response = client.post("/api/agent/generate_activity", json={"requirement": NORMAL_REQUIREMENT})

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "created"


def test_agent_normal_requirement_creates_draft_activity(client):
    response = client.post("/api/agent/generate_activity", json={"requirement": NORMAL_REQUIREMENT})
    activity_id = response.json()["data"]["activity_id"]

    activity_response = client.get(f"/api/activities/{activity_id}")

    assert activity_response.status_code == 200
    assert activity_response.json()["data"]["status"] == "draft"


def test_agent_output_contains_probability_result(client):
    response = client.post("/api/agent/generate_activity", json={"requirement": NORMAL_REQUIREMENT})

    probability_result = response.json()["data"]["probability_result"]
    assert probability_result is not None
    assert "actual_probability" in probability_result


def test_agent_probability_result_contains_pass_field(client):
    response = client.post("/api/agent/generate_activity", json={"requirement": NORMAL_REQUIREMENT})

    assert "pass" in response.json()["data"]["probability_result"]


def test_multiple_normal_requests_create_multiple_activities(client):
    first = client.post("/api/agent/generate_activity", json={"requirement": NORMAL_REQUIREMENT})
    second = client.post("/api/agent/generate_activity", json={"requirement": NORMAL_REQUIREMENT})

    assert first.json()["data"]["activity_id"] != second.json()["data"]["activity_id"]


def test_agent_workflow_depends_on_base_provider_shape():
    workflow = AgentWorkflow(llm_provider=FakeLLMProvider())

    assert workflow.llm_provider.generate(NORMAL_REQUIREMENT)["name"] == "weekend_boss_event"


def test_review_store_is_empty_at_test_start():
    assert list_reviews() == {}
