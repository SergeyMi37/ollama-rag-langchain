"""Модуль для работы с эмбеддингами."""

from langchain_ollama import OllamaEmbeddings

from src.config import settings


def get_embeddings() -> OllamaEmbeddings:
    """Получить модель эмбеддингов."""
    return OllamaEmbeddings(
        model=settings.ollama_embedding_model,
        base_url=settings.ollama_url,
    )
