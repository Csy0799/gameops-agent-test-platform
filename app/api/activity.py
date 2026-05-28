from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.activity import ActivityCreate, ActivityListResponse, ActivityResponse
from app.services import activity_service, operation_log_service

router = APIRouter(prefix="/api/activities", tags=["activities"])


def success_response(data: Any) -> dict[str, Any]:
    return {
        "code": 0,
        "message": "success",
        "data": data,
    }


def to_activity_response(activity: Any) -> dict[str, Any]:
    return ActivityResponse.model_validate(activity).model_dump(mode="json")


@router.post("")
def create_activity(
    activity_in: ActivityCreate,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    activity = activity_service.create_activity(db, activity_in)
    data = to_activity_response(activity)
    operation_log_service.log_operation(
        db,
        operation_type="activity.create",
        target_type="activity",
        target_id=str(activity.id),
        request_data=activity_in.model_dump(mode="json"),
        response_data=data,
        status="success",
    )
    return success_response(data)


@router.get("/{activity_id}")
def get_activity(activity_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    activity = activity_service.get_activity(db, activity_id)
    return success_response(to_activity_response(activity))


@router.get("")
def list_activities(db: Session = Depends(get_db)) -> dict[str, Any]:
    activities = activity_service.list_activities(db)
    payload = ActivityListResponse(
        total=len(activities),
        items=[ActivityResponse.model_validate(activity) for activity in activities],
    ).model_dump(mode="json")
    return success_response(payload)


@router.post("/{activity_id}/publish")
def publish_activity(activity_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    activity = activity_service.publish_activity(db, activity_id)
    data = to_activity_response(activity)
    operation_log_service.log_operation(
        db,
        operation_type="activity.publish",
        target_type="activity",
        target_id=str(activity.id),
        response_data=data,
        status="success",
    )
    return success_response(data)


@router.post("/{activity_id}/rollback")
def rollback_activity(activity_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    activity = activity_service.rollback_activity(db, activity_id)
    data = to_activity_response(activity)
    operation_log_service.log_operation(
        db,
        operation_type="activity.rollback",
        target_type="activity",
        target_id=str(activity.id),
        response_data=data,
        status="success",
    )
    return success_response(data)
