Конечно! Ниже приведён **полный пример RAG-сервиса**, переписанный с Django на **Flask** с использованием:

- **Flask** + **Flask-RESTX** (для REST API)
- **PostgreSQL** (для хранения метаданных — опционально, так как векторы хранятся в Chroma)
- **Ollama** (с поддержкой кастомного URL)
- **Vue.js** (фронтенд, отдельный SPA)
- Структура проекта в стиле **Sakai** (чистая, модульная)

> ⚠️ **Важно**: Chroma — это локальное векторное хранилище на диске. Если вы хотите хранить эмбеддинги **в PostgreSQL**, нужно использовать `pgvector`. Но для простоты и соответствия исходному ТЗ («локальный индекс VectorStoreIndex») мы оставляем **Chroma**, а PostgreSQL используем только для логгирования запросов или метаданных (опционально). Если нужно — могу добавить `pgvector`.

---

## 📁 Структура проекта

```
sakai-rag/
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── rag_engine.py
│   ├── models.py
│   ├── api/
│   │   └── rag.py
│   └── instance/
│       └── chroma_db/     ← векторный индекс
├── data/                   ← ваши .txt файлы
├── frontend/               ← Vue.js SPA
│   ├── public/
│   ├── src/
│   └── package.json
├── requirements.txt
└── .env
```

---

## 1. `requirements.txt`

```txt
Flask==3.0.3
Flask-RESTX==1.3.0
Flask-SQLAlchemy==3.1.1
python-dotenv==1.0.1
langchain==0.2.12
langchain-community==0.2.12
langchain-chroma==0.1.4
chromadb==0.5.5
ollama==0.2.0
psycopg2-binary==2.9.9
```

Установите:

```bash
pip install -r requirements.txt
```

---

## 2. `.env`

```env
FLASK_APP=backend/app.py
FLASK_ENV=development

OLLAMA_URL=http://ваш-адрес:11434
DATA_DIR=./data
CHROMA_PERSIST_DIR=./backend/instance/chroma_db

DATABASE_URL=postgresql://user:password@localhost/rag_db
```

> Замените `ваш-адрес`, `user`, `password`, `rag_db` на свои значения.

---

## 3. `backend/config.py`

```python
# backend/config.py

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
    DATA_DIR = os.getenv("DATA_DIR", "./data")
    CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./backend/instance/chroma_db")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///local.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

---

## 4. `backend/models.py` (опционально — для логгирования)

```python
# backend/models.py

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class QueryLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
```

---

## 5. `backend/rag_engine.py`

```python
# backend/rag_engine.py

import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

_vectorstore = None
_rag_chain = None

def init_rag_engine(ollama_url: str, data_dir: str, persist_dir: str):
    global _vectorstore, _rag_chain

    if _vectorstore is None:
        if os.path.exists(persist_dir) and os.listdir(persist_dir):
            embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=ollama_url)
            _vectorstore = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
        else:
            os.makedirs(data_dir, exist_ok=True)
            if not os.listdir(data_dir):
                raise ValueError("Папка data пуста. Поместите .txt файлы.")

            loader = DirectoryLoader(
                data_dir,
                glob="*.txt",
                loader_cls=TextLoader,
                loader_kwargs={"encoding": "utf-8"}
            )
            docs = loader.load()
            splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            chunks = splitter.split_documents(docs)

            embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=ollama_url)
            _vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=embeddings,
                persist_directory=persist_dir
            )

    if _rag_chain is None:
        retriever = _vectorstore.as_retriever(search_kwargs={"k": 3})
        llm = Ollama(model="llama3", base_url=ollama_url)

        def format_docs(docs):
            return "\n\n".join(d.page_content for d in docs)

        prompt = PromptTemplate.from_template("""
Используй контекст для ответа. Если нет — скажи, что не знаешь.

Контекст:
{context}

Вопрос:
{question}

Ответ:
        """)

        _rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

def ask_question(question: str) -> str:
    if _rag_chain is None:
        raise RuntimeError("RAG engine не инициализирован")
    return _rag_chain.invoke(question)
```

---

## 6. `backend/api/rag.py`

```python
# backend/api/rag.py

from flask_restx import Namespace, Resource, fields
from backend.rag_engine import ask_question
from backend.models import QueryLog, db

api = Namespace('rag', description='RAG queries')

query_model = api.model('Query', {
    'question': fields.String(required=True, description='Вопрос пользователя')
})

@api.route('/ask')
class RAGAsk(Resource):
    @api.expect(query_model)
    @api.response(200, 'Успешный ответ')
    @api.response(400, 'Неверный запрос')
    def post(self):
        question = api.payload.get('question', '').strip()
        if not question:
            api.abort(400, "Вопрос не может быть пустым")

        try:
            answer = ask_question(question)

            # Опционально: сохраняем в БД
            log = QueryLog(question=question, answer=answer)
            db.session.add(log)
            db.session.commit()

            return {'answer': answer}, 200
        except Exception as e:
            api.abort(500, f"Ошибка: {str(e)}")
```

---

## 7. `backend/app.py`

```python
# backend/app.py

from flask import Flask
from flask_restx import Api
from backend.config import Config
from backend.models import db
from backend.rag_engine import init_rag_engine
from backend.api.rag import api as rag_ns
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Инициализация БД
    db.init_app(app)
    with app.app_context():
        db.create_all()

    # Инициализация RAG
    init_rag_engine(
        ollama_url=app.config['OLLAMA_URL'],
        data_dir=app.config['DATA_DIR'],
        persist_dir=app.config['CHROMA_PERSIST_DIR']
    )

    # Настройка API
    api = Api(app, version='1.0', title='Sakai RAG API', description='RAG на Flask + Ollama')
    api.add_namespace(rag_ns, path='/api')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
```

---

## 8. Запуск бэкенда

```bash
# Создайте БД в PostgreSQL (например, через psql):
# CREATE DATABASE rag_db;

# Запустите
flask run --host=0.0.0.0 --port=5000
```

Тест:

```bash
curl -X POST http://localhost:5000/api/rag/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Что в документах?"}'
```

---

## 9. Фронтенд (Vue.js — кратко)

Создайте SPA:

```bash
cd frontend
npm create vue@latest
# выберите опции, установите
cd sakai-rag-frontend
npm install axios
```

`src/views/RagView.vue`:

```vue
<template>
  <div>
    <h2>RAG Query</h2>
    <input v-model="question" @keyup.enter="ask" placeholder="Введите вопрос..." />
    <button @click="ask">Отправить</button>
    <div v-if="answer" class="answer">
      <h3>Ответ:</h3>
      <p>{{ answer }}</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      question: '',
      answer: ''
    };
  },
  methods: {
    async ask() {
      try {
        const res = await axios.post('http://localhost:5000/api/rag/ask', {
          question: this.question
        });
        this.answer = res.data.answer;
      } catch (err) {
        alert('Ошибка: ' + err.response?.data?.message || err.message);
      }
    }
  }
};
</script>
```

Запустите фронтенд:

```bash
npm run dev
```

---

## ✅ Итог

- ✅ Бэкенд на **Flask + Flask-RESTX**
- ✅ Поддержка **кастомного OLLAMA_URL**
- ✅ Данные из `.txt` → **Chroma** (локальный индекс)
- ✅ Опциональное логгирование в **PostgreSQL**
- ✅ Чистая архитектура (Sakai-style)
- ✅ Отдельный **Vue.js** фронтенд

---

### 🔜 Что можно улучшить

- Заменить Chroma на **pgvector** для хранения эмбеддингов в PostgreSQL
- Добавить авторизацию (JWT)
- Добавить health-check эндпоинт
- Docker-контейнеризация

Если нужно — могу добавить `pgvector` или Dockerfile.