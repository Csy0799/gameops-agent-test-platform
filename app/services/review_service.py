import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from sqlalchemy.orm import Session

from app.db.models import AgentReviewRecord, Activity
from app.schemas.activity import ActivityCreate
from app.services.activity_service import create_activity


def _to_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, default=str)


def _from_json(data: Optional[str]) -> Optional[Dict]:
    if not data:
        return None
    return json.loads(data)


def to_review_dict(record: AgentReviewRecord) -> Dict:
    return {
        "review_id": record.review_id,
        "status": record.status,
        "reason": record.reason,
        "config": _from_json(record.config_json),
        "probability_result": _from_json(record.probability_result_json),
        "activity_id": record.activity_id,
        "created_at": record.created_at.isoformat(),
        "updated_at": record.updated_at.isoformat(),
        "reviewed_at": record.reviewed_at.isoformat() if record.reviewed_at else None,
    }


def create_review(
    db: Session,
    config: Dict,
    reason: str,
    probability_result: Optional[Dict] = None,
) -> str:
    review_id = f"review_{uuid4().hex}"
    record = AgentReviewRecord(
        review_id=review_id,
        status="pending",
        reason=reason,
        config_json=_to_json(config),
        probability_result_json=_to_json(probability_result)
        if probability_result is not None
        else None,
    )
    db.add(record)
    db.commit()
    return review_id


def get_review(db: Session, review_id: str) -> Optional[AgentReviewRecord]:
    return (
        db.query(AgentReviewRecord)
        .filter(AgentReviewRecord.review_id == review_id)
        .first()
    )


def list_reviews(
    db: Session,
    status: Optional[str] = None,
    limit: int = 100,
) -> List[AgentReviewRecord]:
    query = db.query(AgentReviewRecord)
    if status:
        query = query.filter(AgentReviewRecord.status == status)
    return query.order_by(AgentReviewRecord.id.desc()).limit(limit).all()


def approve_review(db: Session, review_id: str) -> Dict:
    record = get_review(db, review_id)
    if record is None:
        return {
            "status": "not_found",
            "activity_id": None,
            "review_id": review_id,
            "reason": "review not found",
        }
    if record.status == "approved":
        return {
            "status": "approved",
            "activity_id": record.activity_id,
            "review_id": review_id,
            "reason": None,
        }
    if record.status == "rejected":
        return {
            "status": "rejected",
            "activity_id": None,
            "review_id": review_id,
            "reason": "review already rejected",
        }

    activity: Activity = create_activity(
        db,
        ActivityCreate.model_validate(_from_json(record.config_json)),
    )
    record.status = "approved"
    record.activity_id = activity.id
    record.reviewed_at = datetime.utcnow()
    db.commit()
    return {
        "status": "approved",
        "activity_id": activity.id,
        "review_id": review_id,
        "reason": None,
    }


def reject_review(db: Session, review_id: str) -> Dict:
    record = get_review(db, review_id)
    if record is None:
        return {
            "status": "not_found",
            "activity_id": None,
            "review_id": review_id,
            "reason": "review not found",
        }

    record.status = "rejected"
    record.reviewed_at = datetime.utcnow()
    db.commit()
    return {
        "status": "rejected",
        "activity_id": None,
        "review_id": review_id,
        "reason": "review rejected by human",
    }


def clear_reviews_for_tests(db: Session) -> None:
    db.query(AgentReviewRecord).delete()
    db.commit()
