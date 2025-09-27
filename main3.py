Чтобы использовать **внешний сервер Ollama** (например, `http://другой-адрес:11434`), нужно передать параметр `base_url` в конструкторы `Ollama` и `OllamaEmbeddings`.

Вот обновлённый код для Django-проекта с поддержкой кастомного `OLLAMA_URL`.

---

### ✅ Шаг 1: Настройка URL в `settings.py`

Добавьте в `myproject/settings.py`:

```python
# myproject/settings.py

# ... остальные настройки ...

OLLAMA_URL = "http://другой-адрес:11434"  # ← замените на ваш адрес
```

> 💡 Пример: `OLLAMA_URL = "http://192.168.1.100:11434"`

---

### ✅ Шаг 2: Обновите `rag_engine.py`

Измените файл `rag_app/rag_engine.py`, чтобы он использовал `settings.OLLAMA_URL`:

```python
# rag_app/rag_engine.py

import os
from django.conf import settings
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Глобальные переменные
_vectorstore = None
_rag_chain = None

def get_ollama_base_url():
    return getattr(settings, 'OLLAMA_URL', 'http://localhost:11434')

def get_vectorstore():
    global _vectorstore
    if _vectorstore is not None:
        return _vectorstore

    data_dir = os.path.join(settings.BASE_DIR, "data")
    persist_dir = os.path.join(settings.BASE_DIR, "chroma_db")
    base_url = get_ollama_base_url()

    if os.path.exists(persist_dir) and os.listdir(persist_dir):
        # Загружаем существующий индекс с теми же эмбеддингами
        embeddings = OllamaEmbeddings(
            model="nomic-embed-text",
            base_url=base_url
        )
        _vectorstore = Chroma(
            persist_directory=persist_dir,
            embedding_function=embeddings
        )
    else:
        if not os.path.exists(data_dir):
            raise FileNotFoundError(f"Папка с данными не найдена: {data_dir}")

        loader = DirectoryLoader(
            data_dir,
            glob="*.txt",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"}
        )
        documents = loader.load()

        if not documents:
            raise ValueError("Нет .txt файлов в папке data/")

        text_splitter = CharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            length_function=len
        )
        chunks = text_splitter.split_documents(documents)

        embeddings = OllamaEmbeddings(
            model="nomic-embed-text",
            base_url=base_url
        )
        _vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=persist_dir
        )

    return _vectorstore


def get_rag_chain():
    global _rag_chain
    if _rag_chain is not None:
        return _rag_chain

    base_url = get_ollama_base_url()
    vectorstore = get_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    # Используем внешний Ollama для генерации
    llm = Ollama(
        model="llama3",
        base_url=base_url
    )

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    prompt_template = """
Используй следующий контекст для ответа на вопрос.
Если в контексте нет информации для ответа — скажи, что не знаешь.

Контекст:
{context}

Вопрос:
{question}

Ответ:
"""

    prompt = PromptTemplate.from_template(prompt_template)

    _rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return _rag_chain


def ask_question(question: str) -> str:
    chain = get_rag_chain()
    return chain.invoke(question)
```

---

### ✅ Шаг 3: Убедитесь, что внешний Ollama доступен

На сервере с Ollama должен быть запущен сервис, слушающий **внешние подключения**.

По умолчанию Ollama слушает только `127.0.0.1`. Чтобы разрешить внешние подключения, запустите его так:

```bash
OLLAMA_HOST=0.0.0.0 ollama serve
```

Или на Linux/macOS:

```bash
export OLLAMA_HOST=0.0.0.0
ollama serve
```

> ⚠️ Это открывает API для всех в сети — используйте фаервол или reverse proxy (например, Nginx с аутентификацией) в продакшене.

---

### ✅ Шаг 4: Тестирование

Запустите Django:

```bash
python manage.py runserver
```

И отправьте запрос:

```bash
curl -X POST http://127.0.0.1:8000/rag/ask/ \
  -H "Content-Type: application/json" \
  -d '{"question": "Расскажи о содержимом документов"}'
```

Теперь все вызовы (`эмбеддинги` и `генерация`) идут на указанный вами `OLLAMA_URL`.

---

### 🔄 Дополнительно: поддержка HTTPS и таймаутов

Если нужно — можно добавить таймауты или настроить прокси, но для большинства локальных сетей этого достаточно.

---

Готово! Теперь ваша Django-RAG система работает с удалённым сервером Ollama.