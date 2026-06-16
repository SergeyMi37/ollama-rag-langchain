"""Модуль для работы с LLM."""

from langchain_ollama import OllamaLLM

from src.config import settings


def get_llm() -> OllamaLLM:
    """Получить LLM модель."""
    return OllamaLLM(
        model=settings.ollama_llm_model,
        base_url=settings.ollama_url,
    )
