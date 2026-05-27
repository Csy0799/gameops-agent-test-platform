from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.reward import (
    RewardClaimRequest,
    RewardRecordResponse,
    WalletResponse,
)
from app.services import reward_service

router = APIRouter(tags=["rewards"])


def success_response(data: Any) -> dict[str, Any]:
    return {
        "code": 0,
        "message": "success",
        "data": data,
    }


@router.post("/api/rewards/claim")
def claim_reward(
    claim_in: RewardClaimRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    result = reward_service.claim_reward(db, claim_in)
    return success_response(result.model_dump(mode="json"))


@router.get("/api/users/{user_id}/wallet")
def get_wallet(user_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    wallet = reward_service.get_wallet(db, user_id)
    return success_response(WalletResponse.model_validate(wallet).model_dump(mode="json"))


@router.get("/api/rewards/records")
def list_reward_records(db: Session = Depends(get_db)) -> dict[str, Any]:
    records = reward_service.list_reward_records(db)
    data = [
        RewardRecordResponse.model_validate(record).model_dump(mode="json")
        for record in records
    ]
    return success_response(data)
