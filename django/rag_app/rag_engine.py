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

# Глобальные переменные для кэширования (инициализируются один раз)
_vectorstore = None
_rag_chain = None


def get_vectorstore():
    global _vectorstore
    if _vectorstore is not None:
        return _vectorstore

    data_dir = os.path.join(settings.BASE_DIR, "data")
    persist_dir = os.path.join(settings.BASE_DIR, "chroma_db")

    # Проверяем, существует ли уже сохранённый индекс
    if os.path.exists(persist_dir) and os.listdir(persist_dir):
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        _vectorstore = Chroma(
            persist_directory=persist_dir,
            embedding_function=embeddings
        )
    else:
        # Загружаем и индексируем документы
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

        embeddings = OllamaEmbeddings(model="nomic-embed-text")
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

    vectorstore = get_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    llm = Ollama(model="llama3")

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