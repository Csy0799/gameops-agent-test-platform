import allure
import pytest

from app.agent.fake_llm import FakeLLMProvider
from app.agent.llm_provider import get_llm_provider

pytestmark = [
    pytest.mark.unit,
    pytest.mark.agent,
    allure.feature("Agent Workflow"),
    allure.story("LLM Provider"),
]


def test_default_llm_provider_is_fake(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)

    provider = get_llm_provider()

    assert isinstance(provider, FakeLLMProvider)


def test_fake_llm_provider_selected_by_env(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "fake")

    provider = get_llm_provider()

    assert isinstance(provider, FakeLLMProvider)


def test_openai_provider_without_api_key_raises_clear_error(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.delenv("LLM_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="LLM_API_KEY is required"):
        get_llm_provider()


def test_unknown_llm_provider_raises_clear_error(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "unknown")

    with pytest.raises(RuntimeError, match="unknown LLM_PROVIDER"):
        get_llm_provider()


def test_fake_llm_normal_activity_output_is_stable():
    provider = FakeLLMProvider()
    requirement = "创建一个周末世界Boss活动，掉落概率20%，每人每天最多领取3次，总金币预算1000000"

    first = provider.generate(requirement)
    second = provider.generate(requirement)

    assert first == second
    assert first["name"] == "weekend_boss_event"
    assert first["reward_pool_gold"] == 1000000
    assert first["drop_probability"] == 0.2
    assert first["daily_limit"] == 3


def test_fake_llm_high_budget_sets_high_risk():
    provider = FakeLLMProvider()

    config = provider.generate("创建活动，金币预算2000000，掉率20%，每天最多领取3次")

    assert config["reward_pool_gold"] > 1000000
    assert config["risk_level"] == "high"


def test_fake_llm_high_drop_rate_sets_probability_and_high_risk():
    provider = FakeLLMProvider()

    config = provider.generate("创建活动，金币预算1000000，掉率60%，每天最多领取3次")

    assert config["drop_probability"] == 0.6
    assert config["risk_level"] == "high"


def test_fake_llm_diamond_reward_sets_high_risk():
    provider = FakeLLMProvider()

    config = provider.generate("创建钻石活动，掉率20%，每天最多领取3次")

    assert config["reward_pool_diamond"] > 0
    assert config["risk_level"] == "high"
