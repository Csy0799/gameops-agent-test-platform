import os
from abc import ABC, abstractmethod
from typing import Dict


class BaseLLMProvider(ABC):
    @abstractmethod
    def generate(self, requirement: str) -> Dict:
        raise NotImplementedError


class OpenAICompatibleProvider(BaseLLMProvider):
    def __init__(self) -> None:
        self.api_key = os.getenv("LLM_API_KEY")
        self.base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
        self.model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        if not self.api_key:
            raise RuntimeError("LLM_API_KEY is required for OpenAICompatibleProvider")

    def generate(self, requirement: str) -> Dict:
        # TODO: Call an OpenAI-compatible chat completion API with self.base_url.
        raise RuntimeError("OpenAICompatibleProvider generate is not implemented yet")


def get_llm_provider() -> BaseLLMProvider:
    from app.agent.fake_llm import FakeLLMProvider

    provider_name = os.getenv("LLM_PROVIDER", "fake").lower()
    if provider_name == "fake":
        return FakeLLMProvider()
    if provider_name == "openai":
        return OpenAICompatibleProvider()
    raise RuntimeError(f"unknown LLM_PROVIDER: {provider_name}")
