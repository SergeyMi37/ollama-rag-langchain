"""FastAPI приложение для RAG-сервиса."""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.api.routes import frontend_router, health_router, query_router
from src.config import settings

app = FastAPI(
    title="Ollama RAG Service",
    description="RAG-сервис на основе LangChain и Ollama",
    version="0.1.0",
)

# Подключение роутов
app.include_router(frontend_router)
app.include_router(health_router)
app.include_router(query_router)

# Монтирование статических файлов
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
async def startup_event():
    """Событие при запуске приложения."""
    print(f"OLLAMA_URL: {settings.ollama_url}")
    print(f"LLM Model: {settings.ollama_llm_model}")
    print(f"Embedding Model: {settings.ollama_embedding_model}")
    print(f"Data Dir: {settings.data_dir}")
    print(f"Chroma Persist Dir: {settings.chroma_persist_dir}")
