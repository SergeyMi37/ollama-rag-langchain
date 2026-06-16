"""Роут для RAG-запросов."""

from fastapi import APIRouter

from src.schemas.query import QueryRequest, QueryResponse
from src.services.rag_service import rag_service

router = APIRouter(prefix="/query", tags=["Query"])


@router.post("", response_model=QueryResponse)
async def query(request: QueryRequest) -> QueryResponse:
    """
    Обработать RAG-запрос.

    **question**: Вопрос пользователя
    **top_k**: Количество релевантных документов для поиска (по умолчанию 3)

    Возвращает ответ на основе контекста из векторной базы знаний.
    """
    return rag_service.query(request)
