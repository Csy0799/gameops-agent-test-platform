from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ActivityCreate(BaseModel):
    name: str
    start_time: datetime
    end_time: datetime
    reward_pool_gold: int = Field(default=0, ge=0)
    reward_pool_diamond: int = Field(default=0, ge=0)
    drop_item_id: str
    drop_probability: float = Field(ge=0, le=1)
    daily_limit: int = Field(gt=0)
    pity_threshold: Optional[int] = None
    risk_level: str = "low"

    @model_validator(mode="after")
    def validate_time_range(self) -> "ActivityCreate":
        if self.start_time >= self.end_time:
            raise ValueError("start_time must be earlier than end_time")
        return self


class ActivityResponse(BaseModel):
    id: int
    name: str
    start_time: datetime
    end_time: datetime
    status: str
    reward_pool_gold: int
    reward_pool_diamond: int
    drop_item_id: str
    drop_probability: float
    daily_limit: int
    pity_threshold: Optional[int]
    risk_level: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ActivityListResponse(BaseModel):
    total: int
    items: List[ActivityResponse]
