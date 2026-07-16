from typing import Any

from fastapi import APIRouter, Response, status
from omnixys_cache import CacheClient
from sqlalchemy import text

from chat.config import settings
from chat.database import manager

router = APIRouter()


@router.get("/health")
@router.get("/health/live")
async def health_live() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready")
async def health_ready(response: Response) -> dict[str, Any]:
    checks: dict[str, bool] = {"database": False, "valkey": False}
    try:
        async with manager.session_scope() as session:
            await session.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception:
        pass
    cache = CacheClient(url=settings.cache.url)
    try:
        checks["valkey"] = await cache.ping()
    except Exception:
        pass
    finally:
        await cache.close()
    ready = all(checks.values())
    if not ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {"status": "ok" if ready else "error", "checks": checks}
