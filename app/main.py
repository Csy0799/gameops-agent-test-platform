from typing import Any, Optional

from fastapi import FastAPI

from app.api.activity import router as activity_router
from app.api.reward import router as reward_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logger import get_logger
from app.db.models import Base
from app.db.session import engine

settings = get_settings()
logger = get_logger()


def success_response(data: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    return {
        "code": 0,
        "message": "success",
        "data": data or {},
    }


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, debug=settings.debug)
    register_exception_handlers(app)
    Base.metadata.create_all(bind=engine)

    @app.get(f"{settings.api_prefix}/health")
    async def health_check() -> dict[str, Any]:
        logger.info("Health check requested")
        return success_response({"status": "ok"})

    app.include_router(activity_router)
    app.include_router(reward_router)

    return app


app = create_app()
