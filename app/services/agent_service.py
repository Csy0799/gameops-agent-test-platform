from typing import Dict, Optional

from sqlalchemy.orm import Session

from app.agent.graph import AgentWorkflow
from app.agent.human_review import approve_review, reject_review
from app.agent.llm_provider import BaseLLMProvider
from app.core.exceptions import AppException


def generate_activity_from_requirement(
    db: Session,
    requirement: str,
    llm_provider: Optional[BaseLLMProvider] = None,
) -> Dict:
    workflow = AgentWorkflow(llm_provider=llm_provider)
    return workflow.run(db, requirement)


def review_activity(db: Session, review_id: str, action: str) -> Dict:
    if action == "approve":
        return approve_review(review_id, db)
    if action == "reject":
        return reject_review(review_id)
    raise AppException(message="review action must be approve or reject", code=400)
