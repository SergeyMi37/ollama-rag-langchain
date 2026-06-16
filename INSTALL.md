# Инструкция по установке и запуску

## Быстрый старт

### 1. Установка uv

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Установка зависимостей

```bash
uv sync
```

### 3. Настройка окружения

Файл `.env` уже создан с настройками по умолчанию. При необходимости отредактируйте его.

### 4. Подготовка данных

Поместите `.txt` файлы в папку `./data`

### 5. Запуск сервера

```bash
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Или через скрипт:
```bash
uv run python start.py
```

### 6. Проверка работы

Откройте в браузере:
- **Веб-интерфейс**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **Health check**: http://localhost:8000/health

### 7. Пример запроса

```bash
curl -X POST "http://localhost:8000/query" ^
  -H "Content-Type: application/json" ^
  -d "{\"question\": \"Отсутствует водоснабжение\", \"top_k\": 3}"
```

## Разработка

### Запуск тестов

```bash
uv run pytest tests/ -v
```

### Линтинг и форматирование

```bash
# Проверка
uv run ruff check .

# Форматирование
uv run ruff format .
```

## Требования к Ollama

Перед запуском убедитесь, что Ollama запущен и установлены модели:

```bash
# Проверка запуска Ollama
ollama list

# Установка моделей (если не установлены)
ollama pull llama3.1
ollama pull nomic-embed-text
```

## Структура проекта

```
.
├── src/
│   ├── main.py              # FastAPI приложение
│   ├── config.py            # Настройки
│   ├── api/
│   │   └── routes/
│   │       ├── query.py     # POST /query (REST)
│   │       ├── health.py    # GET /health
│   │       └── frontend.py  # Веб-интерфейс
│   ├── core/
│   │   ├── embeddings.py    # Эмбеддинги
│   │   ├── vectorstore.py   # ChromaDB
│   │   └── llm.py           # LLM
│   ├── services/
│   │   └── rag_service.py   # RAG логика
│   └── schemas/
│       └── query.py         # Pydantic схемы
├── templates/
│   ├── base.html            # Базовый шаблон
│   ├── index.html           # Главная страница
│   └── partials/
│       └── answer.html      # Шаблон ответа
├── static/
│   └── css/
│       └── main.css         # Стили
├── tests/
│   └── test_query.py        # Тесты
├── data/                    # Документы
├── .env                     # Конфигурация
├── pyproject.toml           # Зависимости
├── start.py                 # Скрипт запуска
└── INSTALL.md               # Этот файл
```
