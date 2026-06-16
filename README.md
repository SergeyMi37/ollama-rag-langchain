# Ollama RAG Service 🍁

REST API сервис для RAG (Retrieval-Augmented Generation) на основе LangChain и Ollama.

## Возможности

- 🚀 FastAPI REST API с Swagger документацией
- 🎨 Веб-интерфейс (Jinja2 + HTMX 2 + Alpine.js + Tailwind CSS)
- 🔍 Векторный поиск по документам (ChromaDB)
- 🤖 Генерация ответов через Ollama (Llama 3.1)
- ⚙️ Гибкая конфигурация через .env
- 📦 Управление зависимостями через uv
- 🧹 Линтинг через ruff

## Требования

- Python 3.10+
- Ollama (запущенный сервер)
- Модели Ollama: `llama3.1`, `nomic-embed-text`

## Установка

### 1. Установка uv

```bash
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Клонирование репозитория

```bash
git clone https://github.com/SergeyMi37/ollama-rag-langchain.git
cd ollama-rag-langchain
```

### 3. Установка зависимостей

```bash
uv sync
```

### 4. Настройка окружения

Создайте файл `.env` на основе `env_example`:

```bash
cp env_example .env
```

Отредактируйте `.env` при необходимости.

### 5. Подготовка данных

Поместите `.txt` файлы в папку `./data` (или укажите другую в `.env`).

## Запуск

### Запуск сервера

```bash
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Сервер запустится на `http://localhost:8000`

### Swagger UI

Откройте в браузере: `http://localhost:8000/docs`

## API Endpoints

### REST API

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/` | Веб-интерфейс |
| GET | `/health` | Проверка статуса сервиса |
| POST | `/query` | RAG-запрос с контекстом (JSON) |
| POST | `/query` | RAG-запрос (форма, для HTMX) |

### Пример запроса (REST API)

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "Отсутствует водоснабжение", "top_k": 3}'
```

### Пример ответа

```json
{
  "answer": "Тема 2.2: Проблемы водоснабжения...",
  "sources": [
    {
      "content": "Текст документа...",
      "metadata": {"source": "./data/file.txt"}
    }
  ]
}
```

## Веб-интерфейс

Откройте в браузере: **http://localhost:8000**

### Технологии

- **Jinja2** — серверный рендеринг шаблонов
- **HTMX 2** — интерактивность без виртуального DOM
- **Alpine.js** — реактивность для UI компонентов
- **Tailwind CSS** — стили через CDN (без сборки)

### Особенности

- Мгновенный поиск с индикатором загрузки
- Выбор количества источников (1, 3, 5, 10)
- Раскрывающийся список источников
- Адаптивный дизайн

## Разработка

### Запуск тестов

```bash
uv run pytest tests/ -v
```

### Линтинг

```bash
uv run ruff check .
uv run ruff format .
```

## Структура проекта

```
.
├── src/
│   ├── main.py              # FastAPI приложение
│   ├── config.py            # Настройки из .env
│   ├── api/
│   │   └── routes/
│   │       ├── query.py     # POST /query (REST)
│   │       ├── health.py    # GET /health
│   │       └── frontend.py  # Веб-интерфейс
│   ├── core/
│   │   ├── embeddings.py    # Модель эмбеддингов
│   │   ├── vectorstore.py   # ChromaDB
│   │   └── llm.py           # LLM модель
│   ├── services/
│   │   └── rag_service.py   # Бизнес-логика RAG
│   └── schemas/
│       └── query.py         # Pydantic схемы
├── templates/
│   ├── base.html            # Базовый шаблон
│   ├── index.html           # Главная страница
│   └── partials/
│       └── answer.html      # Частичный шаблон ответа
├── static/
│   └── css/
│       └── main.css         # Дополнительные стили
├── tests/
│   └── test_query.py        # Тесты API
├── data/                    # Документы для индексации
├── .env                     # Конфигурация
├── pyproject.toml           # Зависимости и настройки
└── README.md
```

## Конфигурация (.env)

```env
# Ollama
OLLAMA_URL=http://localhost:11434
OLLAMA_LLM_MODEL=llama3.1
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# Persistence
CHROMA_PERSIST_DIR=./chroma_db
DATA_DIR=./data

# RAG settings
TOP_K=3
CHUNK_SIZE=1024
CHUNK_OVERLAP=50
```

## Благодарности

Спасибо автору статьи на [Habr](https://habr.com/ru/articles/931396/) за основу RAG-системы на LangChain и Ollama.