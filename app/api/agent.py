from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.agent import AgentGenerateRequest, AgentReviewRequest
from app.services import agent_service

router = APIRouter(prefix="/api/agent", tags=["agent"])


def success_response(data: Any) -> dict[str, Any]:
    return {
        "code": 0,
        "message": "success",
        "data": data,
    }


@router.post("/generate_activity")
def generate_activity(
    request: AgentGenerateRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    result = agent_service.generate_activity_from_requirement(db, request.requirement)
    if result["status"] == "rejected":
        return JSONResponse(
            status_code=400,
            content={
                "code": 400,
                "message": "dangerous instruction rejected",
                "data": result,
            },
        )
    return success_response(result)


@router.post("/review/{review_id}")
def review_activity(
    review_id: str,
    request: AgentReviewRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    result = agent_service.review_activity(db, review_id, request.action)
    return success_response(result)
