from typing import Any, Optional

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.agent import AgentGenerateRequest, AgentReviewRequest
from app.services import agent_service, operation_log_service, review_service

router = APIRouter(prefix="/api/agent", tags=["agent"])
admin_router = APIRouter(tags=["admin"])


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
        operation_log_service.log_operation(
            db,
            operation_type="guardrail.reject",
            target_type="agent_review",
            request_data=request.model_dump(mode="json"),
            response_data=result,
            status="rejected",
            message=result["reason"],
        )
        return JSONResponse(
            status_code=400,
            content={
                "code": 400,
                "message": "dangerous instruction rejected",
                "data": result,
            },
        )
    if result["status"] == "pending_review":
        operation_log_service.log_operation(
            db,
            operation_type="agent.review.pending",
            target_type="agent_review",
            target_id=result["review_id"],
            request_data=request.model_dump(mode="json"),
            response_data=result,
            status="pending_review",
            message=result["reason"],
        )
    else:
        operation_log_service.log_operation(
            db,
            operation_type="agent.generate",
            target_type="activity",
            target_id=str(result["activity_id"]),
            request_data=request.model_dump(mode="json"),
            response_data=result,
            status="success",
        )
    return success_response(result)


@router.post("/review/{review_id}")
def review_activity(
    review_id: str,
    request: AgentReviewRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    result = agent_service.review_activity(db, review_id, request.action)
    operation_type = (
        "agent.review.approve" if request.action == "approve" else "agent.review.reject"
    )
    operation_log_service.log_operation(
        db,
        operation_type=operation_type,
        target_type="agent_review",
        target_id=review_id,
        request_data=request.model_dump(mode="json"),
        response_data=result,
        status="success" if result["status"] != "not_found" else "failed",
        message=result.get("reason"),
    )
    return success_response(result)


@router.get("/reviews")
def list_agent_reviews(
    status: Optional[str] = "pending",
    limit: int = 100,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    query_status = None if status == "all" else status
    records = review_service.list_reviews(db, status=query_status, limit=limit)
    items = [review_service.to_review_dict(record) for record in records]
    return success_response({"items": items, "total": len(items)})


@router.get("/reviews/{review_id}")
def get_agent_review(
    review_id: str,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    record = review_service.get_review(db, review_id)
    if record is None:
        return success_response(
            {
                "status": "not_found",
                "review_id": review_id,
                "reason": "review not found",
            }
        )
    return success_response(review_service.to_review_dict(record))


@admin_router.get("/admin/reviews", response_class=HTMLResponse, include_in_schema=False)
def admin_review_queue(db: Session = Depends(get_db)) -> HTMLResponse:
    records = review_service.list_reviews(db, status="pending", limit=100)
    items = [review_service.to_review_dict(record) for record in records]
    rows = "\n".join(_render_review_row(item) for item in items)
    if not rows:
        rows = "<tr><td colspan='11'>No pending reviews.</td></tr>"

    html = f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Review Queue</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #1f2937; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 16px; }}
    th, td {{ border: 1px solid #d1d5db; padding: 8px; text-align: left; vertical-align: top; }}
    th {{ background: #f3f4f6; }}
    button {{ margin-right: 8px; padding: 6px 10px; cursor: pointer; }}
    .approve {{ background: #166534; color: white; border: 0; }}
    .reject {{ background: #991b1b; color: white; border: 0; }}
    .links {{ margin-top: 20px; display: flex; gap: 16px; }}
  </style>
</head>
<body>
  <h1>Review Queue</h1>
  <p>Pending reviews only. Approved or rejected records stay in the database and operation logs.</p>
  <table>
    <thead>
      <tr>
        <th>review_id</th>
        <th>reason</th>
        <th>activity name</th>
        <th>gold</th>
        <th>diamond</th>
        <th>drop probability</th>
        <th>daily limit</th>
        <th>risk level</th>
        <th>probability pass</th>
        <th>created_at</th>
        <th>actions</th>
      </tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>
  <div class="links">
    <a href="/docs">/docs</a>
    <a href="/api/agent/reviews?status=all">/api/agent/reviews?status=all</a>
    <a href="/api/operation-logs">/api/operation-logs</a>
    <a href="/admin/reviews/history">/admin/reviews/history</a>
  </div>
  <script>
    async function review(reviewId, action) {{
      await fetch(`/api/agent/review/${{reviewId}}`, {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify({{ action }})
      }});
      window.location.reload();
    }}
  </script>
</body>
</html>
"""
    return HTMLResponse(content=html)


@admin_router.get(
    "/admin/reviews/history",
    response_class=HTMLResponse,
    include_in_schema=False,
)
def admin_review_history(db: Session = Depends(get_db)) -> HTMLResponse:
    records = review_service.list_reviews(db, status=None, limit=100)
    items = [
        review_service.to_review_dict(record)
        for record in records
        if record.status in {"approved", "rejected"}
    ]
    rows = "\n".join(_render_history_row(item) for item in items)
    if not rows:
        rows = "<tr><td colspan='7'>No reviewed records.</td></tr>"
    html = f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Review History</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #1f2937; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 16px; }}
    th, td {{ border: 1px solid #d1d5db; padding: 8px; text-align: left; }}
    th {{ background: #f3f4f6; }}
  </style>
</head>
<body>
  <h1>Review History</h1>
  <table>
    <thead>
      <tr>
        <th>review_id</th>
        <th>status</th>
        <th>activity_id</th>
        <th>reason</th>
        <th>activity name</th>
        <th>created_at</th>
        <th>reviewed_at</th>
      </tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>
  <p><a href="/admin/reviews">Back to pending queue</a></p>
</body>
</html>
"""
    return HTMLResponse(content=html)


def _render_review_row(item: dict[str, Any]) -> str:
    config = item.get("config") or {}
    probability_result = item.get("probability_result") or {}
    review_id = item["review_id"]
    return f"""
<tr>
  <td>{review_id}</td>
  <td>{item.get("reason")}</td>
  <td>{config.get("name")}</td>
  <td>{config.get("reward_pool_gold")}</td>
  <td>{config.get("reward_pool_diamond")}</td>
  <td>{config.get("drop_probability")}</td>
  <td>{config.get("daily_limit")}</td>
  <td>{config.get("risk_level")}</td>
  <td>{probability_result.get("pass")}</td>
  <td>{item.get("created_at")}</td>
  <td>
    <form onsubmit="event.preventDefault(); review('{review_id}', 'approve');">
      <button class="approve" type="submit">Approve</button>
    </form>
    <form onsubmit="event.preventDefault(); review('{review_id}', 'reject');">
      <button class="reject" type="submit">Reject</button>
    </form>
  </td>
</tr>
"""


def _render_history_row(item: dict[str, Any]) -> str:
    config = item.get("config") or {}
    return f"""
<tr>
  <td>{item.get("review_id")}</td>
  <td>{item.get("status")}</td>
  <td>{item.get("activity_id")}</td>
  <td>{item.get("reason")}</td>
  <td>{config.get("name")}</td>
  <td>{item.get("created_at")}</td>
  <td>{item.get("reviewed_at")}</td>
</tr>
"""
