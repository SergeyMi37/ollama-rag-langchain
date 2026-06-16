"""Роут для проверки здоровья сервиса."""

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check() -> dict:
    """Проверить статус сервиса."""
    return {"status": "ok"}
