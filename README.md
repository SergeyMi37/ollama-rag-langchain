# Ollama RAG Service 🍁

REST API сервис для RAG (Retrieval-Augmented Generation) на основе LangChain и Ollama.

## Возможности

- 🚀 FastAPI REST API с Swagger документацией
- 🎨 Веб-интерфейс (Jinja2 + HTMX 2 + Alpine.js + Tailwind CSS)
- 🔍 Векторный поиск по документам (ChromaDB)
- 🤖 Генерация ответов через Ollama (Llama 3.1)
- ⚙️ Гибкая конфигурация через `.env`
- 📦 Управление зависимостями через `uv`
- 🧹 Линтинг через `ruff`

## Требования

- Python 3.10+
- Ollama (запущенный сервер)
- Модели Ollama: `llama3.1`, `nomic-embed-text`

---

## Установка

### 1. Установка uv

**Windows:**
```bash
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Linux/macOS:**
```bash
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

```bash
cp env_example .env
```

Отредактируйте `.env` при необходимости.

### 5. Подготовка данных

Поместите `.txt` файлы в папку `./data` (или укажите другой путь в `.env`).

---

## Запуск

### Запуск сервера

```bash
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Или через скрипт:
```bash
uv run python start.py
```

### Доступные интерфейсы

| Интерфейс | URL | Описание |
|-----------|-----|----------|
| Веб-интерфейс | http://localhost:8000 | Основной UI |
| Swagger UI | http://localhost:8000/docs | API документация |
| Health check | http://localhost:8000/health | Проверка статуса |

---

## API Endpoints

### REST API (JSON)

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/query` | RAG-запрос с контекстом (JSON) |
| GET | `/health` | Проверка статуса сервиса |

**Пример запроса:**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "Отсутствует водоснабжение", "top_k": 3}'
```

**Пример ответа:**
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

### Веб-интерфейс (HTMX)

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/` | Главная страница с формой поиска |
| POST | `/query` | Обработка запроса (форма) |

---

## Технологии фронтенда

### Стек

| Технология | Версия | Назначение |
|------------|--------|------------|
| Jinja2 | 3.1.2+ | Серверный рендеринг шаблонов |
| HTMX | 2.0.4 | AJAX-запросы без JavaScript |
| Alpine.js | 3.x | Реактивность UI |
| Tailwind CSS | CDN | Стилизация без сборки |

### Как работает

```
Пользователь → Браузер → FastAPI → RAG Service → Ollama
```

1. **Jinja2** — рендерит HTML-шаблоны на сервере
2. **HTMX** — отправляет POST-запросы при отправке формы, заменяет часть страницы
3. **Alpine.js** — управляет состоянием (показать/скрыть, загрузка)
4. **Tailwind CSS** — стилизация через классы в HTML

### Пример работы HTMX

```html
<form hx-post="/query" hx-target="#results" hx-swap="innerHTML">
    <textarea name="question"></textarea>
    <button type="submit">Найти</button>
</form>
<div id="results"></div>
```

При нажатии кнопки HTMX автоматически:
1. Отправляет POST-запрос на `/query`
2. Получает HTML-ответ
3. Заменяет содержимое `#results`

---

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
│       └── answer.html      # Шаблон ответа
├── static/
│   └── css/
│       └── main.css         # Дополнительные стили
├── tests/
│   └── test_query.py        # Тесты API
├── data/                    # Документы для индексации
├── .env                     # Конфигурация
├── pyproject.toml           # Зависимости и настройки
├── start.py                 # Скрипт запуска
└── README.md
```

---

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

---

## Разработка

### Запуск тестов

```bash
uv run pytest tests/ -v
```

### Линтинг и форматирование

```bash
uv run ruff check .
uv run ruff format .
```

---

## Благодарности

Спасибо автору статьи на [Habr](https://habr.com/ru/articles/931396/) за основу RAG-системы на LangChain и Ollama.
