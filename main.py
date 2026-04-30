import os
import shutil
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

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
# if os.path.exists(persist_dir):
#     shutil.rmtree(persist_dir)
#     print(f"Удалена старая база: {persist_dir}")

# 5. Создание и сохранение локального векторного индекса (Chroma)
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db"  # сохраняем локально
)

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
