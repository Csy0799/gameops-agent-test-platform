from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.db.models import Activity, RewardRecord, UserWallet
from app.schemas.reward import RewardClaimRequest, RewardClaimResponse
from app.services.idempotency_service import get_existing_record_by_key

REWARD_GOLD = 100
REWARD_DIAMOND = 0


def get_or_create_wallet(db: Session, user_id: str) -> UserWallet:
    wallet = db.query(UserWallet).filter(UserWallet.user_id == user_id).first()
    if wallet is not None:
        return wallet

    wallet = UserWallet(user_id=user_id, gold=0, diamond=0)
    db.add(wallet)
    db.flush()
    return wallet


def get_wallet(db: Session, user_id: str) -> UserWallet:
    wallet = get_or_create_wallet(db, user_id)
    db.commit()
    db.refresh(wallet)
    return wallet


def list_reward_records(db: Session) -> List[RewardRecord]:
    return db.query(RewardRecord).order_by(RewardRecord.id.asc()).all()


def check_daily_limit(db: Session, user_id: str, activity: Activity) -> None:
    now = datetime.utcnow()
    day_start = datetime(now.year, now.month, now.day)
    day_end = day_start + timedelta(days=1)
    success_count = (
        db.query(RewardRecord)
        .filter(
            RewardRecord.user_id == user_id,
            RewardRecord.activity_id == activity.id,
            RewardRecord.status == "success",
            RewardRecord.created_at >= day_start,
            RewardRecord.created_at < day_end,
        )
        .count()
    )
    if success_count >= activity.daily_limit:
        raise AppException(message="daily claim limit exceeded", code=400)


def calculate_reward(activity: Activity) -> Tuple[int, int]:
    return REWARD_GOLD, REWARD_DIAMOND


def _build_claim_response(
    record: RewardRecord,
    wallet: UserWallet,
    duplicated: bool,
) -> RewardClaimResponse:
    return RewardClaimResponse(
        user_id=record.user_id,
        activity_id=record.activity_id,
        reward_gold=record.reward_gold,
        reward_diamond=record.reward_diamond,
        wallet_gold=wallet.gold,
        wallet_diamond=wallet.diamond,
        idempotency_key=record.idempotency_key,
        duplicated=duplicated,
    )


def _validate_activity_can_claim(activity: Optional[Activity]) -> Activity:
    if activity is None:
        raise AppException(message="activity not found", code=404)
    if activity.status != "published":
        raise AppException(message="only published activity can be claimed", code=400)

    now = datetime.utcnow()
    if now < activity.start_time:
        raise AppException(message="activity has not started", code=400)
    if now > activity.end_time:
        raise AppException(message="activity has ended", code=400)
    return activity


def claim_reward(db: Session, claim_in: RewardClaimRequest) -> RewardClaimResponse:
    existing_record = get_existing_record_by_key(db, claim_in.idempotency_key)
    if existing_record is not None:
        wallet = get_or_create_wallet(db, existing_record.user_id)
        db.commit()
        db.refresh(wallet)
        return _build_claim_response(existing_record, wallet, duplicated=True)

    try:
        activity = _validate_activity_can_claim(db.get(Activity, claim_in.activity_id))
        check_daily_limit(db, claim_in.user_id, activity)
        reward_gold, reward_diamond = calculate_reward(activity)

        if activity.reward_pool_gold < reward_gold:
            raise AppException(message="reward gold pool is insufficient", code=400)
        if activity.reward_pool_diamond < reward_diamond:
            raise AppException(message="reward diamond pool is insufficient", code=400)

        wallet = get_or_create_wallet(db, claim_in.user_id)
        activity.reward_pool_gold -= reward_gold
        activity.reward_pool_diamond -= reward_diamond
        wallet.gold += reward_gold
        wallet.diamond += reward_diamond

        record = RewardRecord(
            user_id=claim_in.user_id,
            activity_id=activity.id,
            idempotency_key=claim_in.idempotency_key,
            reward_gold=reward_gold,
            reward_diamond=reward_diamond,
            status="success",
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        db.refresh(wallet)
        return _build_claim_response(record, wallet, duplicated=False)
    except Exception:
        db.rollback()
        raise
