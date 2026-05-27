from typing import Any

from fastapi import APIRouter

from app.schemas.probability import ProbabilityValidateRequest
from app.services.probability_service import probability_service

router = APIRouter(prefix="/api/tools/probability", tags=["probability"])


def success_response(data: Any) -> dict[str, Any]:
    return {
        "code": 0,
        "message": "success",
        "data": data,
    }


@router.post("/validate")
def validate_probability(request: ProbabilityValidateRequest) -> dict[str, Any]:
    result = probability_service.validate_probability(request.model_dump())
    return success_response(result)
