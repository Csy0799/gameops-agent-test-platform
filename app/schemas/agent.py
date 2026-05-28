from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class AgentGenerateRequest(BaseModel):
    requirement: str


class AgentGenerateResponse(BaseModel):
    status: str
    activity_id: Optional[int]
    review_id: Optional[str]
    reason: Optional[str]
    config: Optional[Dict[str, Any]]
    probability_result: Optional[Dict[str, Any]]


class AgentReviewRequest(BaseModel):
    action: str = Field(pattern="^(approve|reject)$")


class AgentReviewResponse(BaseModel):
    status: str
    activity_id: Optional[int]
    review_id: str
    reason: Optional[str]
