import json
import os
import shutil

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.llms import Ollama
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Путь к папке с .txt файлами
DATA_DIR = "./data"  # замените на свой путь

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
print('-----',OLLAMA_URL)

# 1. Загрузка всех .txt файлов из папки
loader = DirectoryLoader(DATA_DIR,
                        glob="*.txt",
                        loader_kwargs={"encoding": "utf-8"},
                        loader_cls=TextLoader)
documents = loader.load()

# 2. Разделение документов на чанки (~256 символов)
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1024,
    chunk_overlap=50,
    separators=["\n\n", "\n", "。", ".", " ", ""],
    length_function=len,
)
chunks = text_splitter.split_documents(documents)

# 3. Создание эмбеддингов через Ollama (используем nomic-embed-text для 768-мерных векторов)
embeddings = OllamaEmbeddings(model="nomic-embed-text",
            base_url=OLLAMA_URL
            )

# 4. Удаление старой базы данных если она была создана с другой размерностью

persist_dir = "./chroma_db"
metadata_file = os.path.join(persist_dir, "embedding_size.json")

def get_embedding_dimension():
    """Получить размерность эмбеддингов от текущей модели"""
    test_text = ["test"]
    embedding = embeddings.embed_documents(test_text)[0]
    return len(embedding)

def should_recreate_database():
    """Проверить нужно ли пересоздавать базу данных"""
    if not os.path.exists(persist_dir):
        return True

    current_dim = get_embedding_dimension()

    if os.path.exists(metadata_file):
        try:
            with open(metadata_file, encoding='utf-8') as f:
                saved_dim = json.load(f).get("embedding_dimension")
            if saved_dim == current_dim:
                print(f"Размерность совпадает ({current_dim}). Используем существующую базу.")
                return False
            else:
                print(f"Размерность изменилась: была {saved_dim}, стала {current_dim}. Пересоздаём базу.")
                return True
        except (OSError, json.JSONDecodeError) as e:
            print(f"Ошибка чтения метаданных: {e}. Пересоздаём базу.")
            return True
    else:
        print("Файл метаданных не найден. Пересоздаём базу.")
        return True

if should_recreate_database():
    if os.path.exists(persist_dir):
        shutil.rmtree(persist_dir)
        print(f"Удалена старая база: {persist_dir}")

# 5. Создание и сохранение локального векторного индекса (Chroma)
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db"  # сохраняем локально
)

# Сохраняем размерность эмбеддингов в файл метаданных
os.makedirs(persist_dir, exist_ok=True)
embedding_dim = get_embedding_dimension()
with open(metadata_file, 'w', encoding='utf-8') as f:
    json.dump({"embedding_dimension": embedding_dim}, f)
print(f"Сохранена размерность эмбеддингов: {embedding_dim}")

# 6. Настройка retriever (возвращает топ-3 релевантных чанка)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# 7. Инициализация LLM (например, llama3)
llm = Ollama(model="llama3.1",
            base_url=OLLAMA_URL
            )

# 8. Формирование цепочки RAG
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

# 9. Пример использования
if __name__ == "__main__":
    txt = input("Введите тему обращения: ")
    #txt = 'Отсутствует водоснабжение'
    question =f"Используя исходные документы, выбери номер темы, который больше всего подходит для текста: {txt}. В Ответ предоставь только номер темы."
    answer = rag_chain.invoke(question)
    print("\nОтвет:\n", answer)
