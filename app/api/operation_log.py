from typing import Any, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import operation_log_service

router = APIRouter(prefix="/api/operation-logs", tags=["operation-logs"])


class OperationLogCleanupRequest(BaseModel):
    retention_days: Optional[int] = None


def success_response(data: Any) -> dict[str, Any]:
    return {
        "code": 0,
        "message": "success",
        "data": data,
    }


def to_log_dict(log) -> dict[str, Any]:
    return {
        "id": log.id,
        "trace_id": log.trace_id,
        "actor": log.actor,
        "operation_type": log.operation_type,
        "target_type": log.target_type,
        "target_id": log.target_id,
        "status": log.status,
        "message": log.message,
        "created_at": log.created_at.isoformat(),
    }


@router.get("")
def list_operation_logs(
    operation_type: Optional[str] = None,
    target_type: Optional[str] = None,
    actor: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    logs = operation_log_service.list_logs(
        db,
        operation_type=operation_type,
        target_type=target_type,
        actor=actor,
        limit=limit,
    )
    return success_response([to_log_dict(log) for log in logs])


@router.post("/cleanup")
def cleanup_operation_logs(
    request: OperationLogCleanupRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    deleted_count = operation_log_service.cleanup_expired_logs(
        db,
        retention_days=request.retention_days,
    )
    return success_response({"deleted_count": deleted_count})
