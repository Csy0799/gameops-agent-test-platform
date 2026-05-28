import json
from datetime import datetime, timedelta
from typing import Any, List, Optional

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import OperationLog


def _to_json(data: Any) -> Optional[str]:
    if data is None:
        return None
    return json.dumps(data, ensure_ascii=False, default=str)


def log_operation(
    db: Session,
    operation_type: str,
    target_type: str,
    target_id: Optional[str] = None,
    actor: str = "system",
    request_data: Any = None,
    response_data: Any = None,
    status: str = "success",
    message: Optional[str] = None,
    trace_id: Optional[str] = None,
) -> Optional[OperationLog]:
    if not get_settings().enable_operation_log:
        return None

    try:
        log = OperationLog(
            trace_id=trace_id,
            actor=actor,
            operation_type=operation_type,
            target_type=target_type,
            target_id=str(target_id) if target_id is not None else None,
            request_json=_to_json(request_data),
            response_json=_to_json(response_data),
            status=status,
            message=message,
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
    except Exception:
        db.rollback()
        return None


def list_logs(
    db: Session,
    operation_type: Optional[str] = None,
    target_type: Optional[str] = None,
    actor: Optional[str] = None,
    limit: int = 100,
) -> List[OperationLog]:
    query = db.query(OperationLog)
    if operation_type:
        query = query.filter(OperationLog.operation_type == operation_type)
    if target_type:
        query = query.filter(OperationLog.target_type == target_type)
    if actor:
        query = query.filter(OperationLog.actor == actor)
    return query.order_by(OperationLog.id.desc()).limit(limit).all()


def cleanup_expired_logs(
    db: Session,
    retention_days: Optional[int] = None,
) -> int:
    days = retention_days or get_settings().operation_log_retention_days
    cutoff = datetime.utcnow() - timedelta(days=days)
    deleted = db.query(OperationLog).filter(OperationLog.created_at < cutoff).delete()
    db.commit()
    return deleted
