from typing import Dict, Optional
from uuid import uuid4

from sqlalchemy.orm import Session

from app.db.models import Activity
from app.schemas.activity import ActivityCreate
from app.services.activity_service import create_activity

PENDING_REVIEWS: Dict[str, Dict] = {}


def create_review(
    config: Dict,
    reason: str,
    probability_result: Optional[Dict] = None,
) -> str:
    review_id = f"review_{uuid4().hex}"
    PENDING_REVIEWS[review_id] = {
        "config": config,
        "reason": reason,
        "probability_result": probability_result,
    }
    return review_id


def get_review(review_id: str) -> Optional[Dict]:
    return PENDING_REVIEWS.get(review_id)


def approve_review(review_id: str, db: Session) -> Dict:
    review = PENDING_REVIEWS.pop(review_id, None)
    if review is None:
        return {
            "status": "not_found",
            "activity_id": None,
            "review_id": review_id,
            "reason": "review not found",
        }

    activity: Activity = create_activity(db, ActivityCreate.model_validate(review["config"]))
    return {
        "status": "approved",
        "activity_id": activity.id,
        "review_id": review_id,
        "reason": None,
    }


def reject_review(review_id: str) -> Dict:
    review = PENDING_REVIEWS.pop(review_id, None)
    if review is None:
        return {
            "status": "not_found",
            "activity_id": None,
            "review_id": review_id,
            "reason": "review not found",
        }

    return {
        "status": "rejected",
        "activity_id": None,
        "review_id": review_id,
        "reason": "review rejected by human",
    }


def clear_reviews() -> None:
    PENDING_REVIEWS.clear()


def list_reviews() -> Dict[str, Dict]:
    return dict(PENDING_REVIEWS)
