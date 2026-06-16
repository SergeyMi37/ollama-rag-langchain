"""Конфигурация приложения."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения."""

    # Ollama
    ollama_url: str = "http://localhost:11434"
    ollama_llm_model: str = "llama3.1"
    ollama_embedding_model: str = "nomic-embed-text"

    # Persistence
    chroma_persist_dir: str = "./chroma_db"
    data_dir: str = "./data"

    # RAG settings
    top_k: int = 3
    chunk_size: int = 1024
    chunk_overlap: int = 50

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


settings = Settings()
