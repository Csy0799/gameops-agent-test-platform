from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from pydantic import ValidationError

from app.core.exceptions import AppException
from app.schemas.activity import ActivityCreate
from app.services.probability_service import probability_service

DANGEROUS_WORDS = [
    "直接执行sql",
    "执行sql",
    "绕过审核",
    "无限奖励",
    "删除数据库",
    "drop table",
    "bypass review",
    "unlimited reward",
    "delete database",
]


def guardrail_check(requirement: str) -> bool:
    lowered = requirement.lower()
    return any(word in lowered for word in DANGEROUS_WORDS)


def enrich_default_fields(config: Dict) -> Dict:
    enriched = dict(config)
    now = datetime.utcnow()
    enriched.setdefault("start_time", now - timedelta(hours=1))
    enriched.setdefault("end_time", now + timedelta(days=7))
    return enriched


def validate_activity_rule(config: Dict) -> ActivityCreate:
    try:
        return ActivityCreate.model_validate(config)
    except ValidationError as exc:
        raise AppException(message="activity config validation failed", code=400) from exc


def simulate_probability(config: Dict) -> Dict:
    return probability_service.validate_drop_rate(
        probability=config["drop_probability"],
        sample_size=10000,
        tolerance=0.02,
        seed=42,
    )


def check_budget_risk(config: Dict, probability_result: Dict) -> Tuple[bool, List[str]]:
    reasons = []
    if config.get("risk_level") == "high":
        reasons.append("risk_level is high")
    if config.get("reward_pool_gold", 0) > 1000000:
        reasons.append("reward_pool_gold exceeds 1000000")
    if config.get("drop_probability", 0) > 0.5:
        reasons.append("drop_probability exceeds 0.5")
    if config.get("reward_pool_diamond", 0) > 0:
        reasons.append("diamond reward requires review")
    if probability_result.get("pass") is False:
        reasons.append("probability simulation failed")
    return bool(reasons), reasons
