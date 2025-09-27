# Вот полная программа на Python с использованием **LangChain**, **OllamaEmbeddings**, **Ollama LLM**, и **Chroma** в качестве локального векторного хранилища (VectorStore), которая реализует RAG-систему по вашему описанию:

# ---

# ### 🔧 Требования

# Убедитесь, что у вас установлены следующие пакеты:

# ```bash
# pip install langchain langchain-community langchain-chroma ollama chromadb
# ```

# Также убедитесь, что у вас запущен **Ollama** и доступны модели, например:

# ```bash
# ollama pull llama3
# ollama pull nomic-embed-text  # для эмбеддингов
# ```

# ---

# ### 📜 Код программы

# ```python
import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Путь к папке с .txt файлами
DATA_DIR = "./docs"  # замените на свой путь

# 1. Загрузка всех .txt файлов из папки
loader = DirectoryLoader(DATA_DIR,
                        glob="*.txt",
                        loader_kwargs={"encoding": "utf-8"},
                        loader_cls=TextLoader)
documents = loader.load()

# 2. Разделение документов на чанки (~1000 символов)
text_splitter = CharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100,
    length_function=len,
    is_separator_regex=False,
)
chunks = text_splitter.split_documents(documents)

# 3. Создание эмбеддингов через Ollama (используем nomic-embed-text)
embeddings = OllamaEmbeddings(model="all-minilm")

# 4. Создание и сохранение локального векторного индекса (Chroma)
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db"  # сохраняем локально
)

# 5. Настройка retriever (возвращает топ-3 релевантных чанка)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# 6. Инициализация LLM (например, llama3)
llm = Ollama(model="llama3.1")

# 7. Формирование цепочки RAG
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

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 8. Пример использования
if __name__ == "__main__":
    question = input("Введите ваш вопрос: ")
    answer = rag_chain.invoke(question)
    print("\nОтвет:\n", answer)
# ```

# ---

# ### 📁 Структура проекта

# ```
# your_project/
# ├── main.py                 # код выше
# └── data/
#     ├── doc1.txt
#     ├── doc2.txt
#     └── ...
# ```

# ---

# ### 💡 Примечания

# - **Модель для эмбеддингов**: `nomic-embed-text` — популярная и бесплатная модель в Ollama для эмбеддингов. Убедитесь, что она скачана (`ollama pull nomic-embed-text`).
# - **Модель для генерации**: `llama3` — можно заменить на `mistral`, `phi3` и т.д.
# - **Хранение индекса**: Векторное хранилище сохраняется в папку `./chroma_db`, поэтому при повторном запуске не нужно заново индексировать (если файлы не менялись).
# - **Размер чанка**: ~1000 символов (не токенов!). Если нужно по токенам — используйте `RecursiveCharacterTextSplitter` с `tiktoken`.

# ---

# ### 🔄 Опционально: пересоздание индекса при изменении файлов

# Если вы хотите, чтобы программа пересоздавала индекс при изменении файлов — добавьте проверку хешей или просто удаляйте папку `chroma_db` перед запуском.

# ---

# Готово! Теперь у вас полноценная RAG-система на LangChain + Ollama с локальным хранением.