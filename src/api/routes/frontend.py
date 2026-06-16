"""Роуты для фронтенда."""

import os
from pathlib import Path
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader

from src.schemas.query import QueryRequest
from src.services.rag_service import rag_service

router = APIRouter(tags=["Frontend"])

# Путь к папке templates относительно корня проекта
templates_dir = Path(os.getcwd()) / "templates"

# Создаем Jinja2 Environment с FileSystemLoader
env = Environment(loader=FileSystemLoader(str(templates_dir)), auto_reload=True)
env.cache_size = 0


@router.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    """Главная страница."""
    template = env.get_template("index.html")
    return HTMLResponse(template.render(request=request))


@router.post("/query", response_class=HTMLResponse)
async def query_htmx(
    request: Request,
    question: str = Form(...),
    top_k: int = Form(default=3),
) -> HTMLResponse:
    """Обработка запроса через HTMX."""
    query_request = QueryRequest(question=question, top_k=top_k)
    response = rag_service.query(query_request)

    template = env.get_template("partials/answer.html")
    return HTMLResponse(
        template.render(
            request=request,
            answer=response.answer,
            sources=response.sources,
            question=question,
        )
    )


@router.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    """Главная страница."""
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/query", response_class=HTMLResponse)
async def query_htmx(
    request: Request,
    question: str = Form(...),
    top_k: int = Form(default=3),
) -> HTMLResponse:
    """Обработка запроса через HTMX."""
    query_request = QueryRequest(question=question, top_k=top_k)
    response = rag_service.query(query_request)

    return templates.TemplateResponse(
        "partials/answer.html",
        {
            "request": request,
            "answer": response.answer,
            "sources": response.sources,
            "question": question,
        },
    )
