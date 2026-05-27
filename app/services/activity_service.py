from typing import List

from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.db.models import Activity
from app.schemas.activity import ActivityCreate


def create_activity(db: Session, activity_in: ActivityCreate) -> Activity:
    activity = Activity(
        **activity_in.model_dump(),
        status="draft",
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


def get_activity(db: Session, activity_id: int) -> Activity:
    activity = db.get(Activity, activity_id)
    if activity is None:
        raise AppException(message="activity not found", code=404)
    return activity


def list_activities(db: Session) -> List[Activity]:
    return db.query(Activity).order_by(Activity.id.asc()).all()


def publish_activity(db: Session, activity_id: int) -> Activity:
    activity = get_activity(db, activity_id)
    if activity.status == "published":
        raise AppException(message="activity already published", code=400)

    activity.status = "published"
    db.commit()
    db.refresh(activity)
    return activity


def rollback_activity(db: Session, activity_id: int) -> Activity:
    activity = get_activity(db, activity_id)
    if activity.status != "published":
        raise AppException(message="only published activity can be rolled back", code=400)

    activity.status = "rolled_back"
    db.commit()
    db.refresh(activity)
    return activity
