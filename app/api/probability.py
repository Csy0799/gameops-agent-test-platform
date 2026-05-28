from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.probability import ProbabilityValidateRequest
from app.services import operation_log_service
from app.services.probability_service import probability_service

router = APIRouter(prefix="/api/tools/probability", tags=["probability"])


def success_response(data: Any) -> dict[str, Any]:
    return {
        "code": 0,
        "message": "success",
        "data": data,
    }


@router.post("/validate")
def validate_probability(
    request: ProbabilityValidateRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    result = probability_service.validate_probability(request.model_dump())
    operation_log_service.log_operation(
        db,
        operation_type="probability.validate",
        target_type="probability",
        request_data=request.model_dump(mode="json"),
        response_data=result,
        status="success",
    )
    return success_response(result)
