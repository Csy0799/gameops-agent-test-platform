from typing import Optional

from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.db.models import RewardRecord


def get_existing_record_by_key(
    db: Session,
    idempotency_key: str,
) -> Optional[RewardRecord]:
    return (
        db.query(RewardRecord)
        .filter(RewardRecord.idempotency_key == idempotency_key)
        .first()
    )


def ensure_idempotency_key_available(db: Session, idempotency_key: str) -> None:
    existing_record = get_existing_record_by_key(db, idempotency_key)
    if existing_record is not None:
        raise AppException(message="idempotency key already used", code=400)
