"""Тесты для API запросов."""

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_health_check():
    """Тест проверки здоровья."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_query_basic():
    """Тест базового запроса."""
    request_data = {
        "question": "Какие темы доступны?",
        "top_k": 3,
    }
    response = client.post("/query", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data


def test_query_validation():
    """Тест валидации запроса."""
    # Пустой вопрос
    response = client.post("/query", json={"question": ""})
    assert response.status_code == 422

    # Отсутствие вопроса
    response = client.post("/query", json={})
    assert response.status_code == 422
