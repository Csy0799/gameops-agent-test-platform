import re
from typing import Dict

from app.agent.llm_provider import BaseLLMProvider


class FakeLLMProvider(BaseLLMProvider):
    def generate(self, requirement: str) -> Dict:
        text = requirement.lower()
        config = {
            "name": "weekend_boss_event",
            "reward_pool_gold": 1000000,
            "reward_pool_diamond": 0,
            "drop_item_id": "rare_box",
            "drop_probability": 0.2,
            "daily_limit": 3,
            "pity_threshold": 50,
            "risk_level": "medium",
        }

        probability = self._extract_percent(requirement)
        if probability is not None:
            config["drop_probability"] = probability

        daily_limit = self._extract_daily_limit(requirement)
        if daily_limit is not None:
            config["daily_limit"] = daily_limit

        budget = self._extract_gold_budget(requirement)
        if budget is not None:
            config["reward_pool_gold"] = budget

        if "金币预算超过1000000" in requirement or "高额返利" in requirement:
            config["reward_pool_gold"] = max(config["reward_pool_gold"], 2000000)

        if "钻石" in requirement or "diamond" in text:
            config["reward_pool_diamond"] = 1000

        if (
            config["reward_pool_gold"] > 1000000
            or config["drop_probability"] >= 0.6
            or config["reward_pool_diamond"] > 0
        ):
            config["risk_level"] = "high"

        return config

    def _extract_percent(self, requirement: str):
        match = re.search(r"(?:掉落概率|掉率)\s*(\d+(?:\.\d+)?)%", requirement, re.IGNORECASE)
        if match:
            return float(match.group(1)) / 100
        return None

    def _extract_daily_limit(self, requirement: str):
        match = re.search(r"每天最多领取\s*(\d+)\s*次", requirement)
        if match:
            return int(match.group(1))
        return None

    def _extract_gold_budget(self, requirement: str):
        match = re.search(r"金币预算\s*(\d+)", requirement)
        if match:
            return int(match.group(1))
        return None
