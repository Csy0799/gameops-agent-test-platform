from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class RewardClaimRequest(BaseModel):
    user_id: str = Field(min_length=1)
    activity_id: int
    idempotency_key: str = Field(min_length=1)


class RewardClaimResponse(BaseModel):
    user_id: str
    activity_id: int
    reward_gold: int
    reward_diamond: int
    wallet_gold: int
    wallet_diamond: int
    idempotency_key: str
    duplicated: bool


class WalletResponse(BaseModel):
    user_id: str
    gold: int
    diamond: int

    model_config = ConfigDict(from_attributes=True)


class RewardRecordResponse(BaseModel):
    id: int
    user_id: str
    activity_id: int
    idempotency_key: str
    reward_gold: int
    reward_diamond: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
