"""Ядро RAG-системы."""

from src.core.embeddings import get_embeddings
from src.core.llm import get_llm
from src.core.vectorstore import get_vectorstore

__all__ = ["get_embeddings", "get_vectorstore", "get_llm"]
