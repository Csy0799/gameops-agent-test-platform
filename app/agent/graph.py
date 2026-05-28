from typing import Dict, Optional

from sqlalchemy.orm import Session

from app.agent.llm_provider import BaseLLMProvider, get_llm_provider
from app.agent.tools import (
    check_budget_risk,
    enrich_default_fields,
    guardrail_check,
    simulate_probability,
    validate_activity_rule,
)
from app.core.exceptions import AppException
from app.services.activity_service import create_activity
from app.services.review_service import create_review


class AgentWorkflow:
    def __init__(self, llm_provider: Optional[BaseLLMProvider] = None) -> None:
        self.llm_provider = llm_provider or get_llm_provider()

    def run(self, db: Session, requirement: str) -> Dict:
        parsed_requirement = self.parse_requirement(requirement)
        if guardrail_check(parsed_requirement):
            return {
                "status": "rejected",
                "activity_id": None,
                "review_id": None,
                "reason": "dangerous instruction detected",
                "config": None,
                "probability_result": None,
            }

        config = self.llm_provider.generate(parsed_requirement)
        config = enrich_default_fields(config)
        activity_in = validate_activity_rule(config)
        probability_result = simulate_probability(config)
        high_risk, reasons = check_budget_risk(config, probability_result)

        if high_risk:
            review_id = create_review(
                db=db,
                config=activity_in.model_dump(),
                reason="high risk activity requires human review",
                probability_result=probability_result,
            )
            return {
                "status": "pending_review",
                "activity_id": None,
                "review_id": review_id,
                "reason": "high risk activity requires human review",
                "config": activity_in.model_dump(),
                "probability_result": probability_result,
            }

        activity = create_activity(db, activity_in)
        return {
            "status": "created",
            "activity_id": activity.id,
            "review_id": None,
            "reason": None,
            "config": activity_in.model_dump(),
            "probability_result": probability_result,
        }

    def parse_requirement(self, requirement: str) -> str:
        if requirement is None or not requirement.strip():
            raise AppException(message="requirement must not be empty", code=400)
        return requirement.strip()
