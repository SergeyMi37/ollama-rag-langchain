"""Схемы для запросов и ответов."""

from pydantic import BaseModel, Field


class SourceDocument(BaseModel):
    """Исходный документ."""

    content: str = Field(description="Содержимое документа")
    metadata: dict = Field(default_factory=dict, description="Метаданные документа")


class QueryRequest(BaseModel):
    """Запрос к RAG-системе."""

    question: str = Field(description="Вопрос пользователя", min_length=1)
    top_k: int = Field(default=3, description="Количество релевантных документов", ge=1, le=10)


class QueryResponse(BaseModel):
    """Ответ RAG-системы."""

    answer: str = Field(description="Ответ на вопрос")
    sources: list[SourceDocument] = Field(default_factory=list, description="Исходные документы")
