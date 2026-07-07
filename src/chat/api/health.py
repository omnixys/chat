from fastapi import APIRouter
from sqlalchemy import text

from chat.database import get_db

router = APIRouter()


@router.get("/health")
@router.get("/health/live")
async def health_live():
    return {"status": "ok"}


@router.get("/health/ready")
async def health_ready():
    try:
        async for session in get_db():
            await session.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
