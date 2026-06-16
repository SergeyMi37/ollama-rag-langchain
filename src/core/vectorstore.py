"""Модуль для работы с векторным хранилищем."""

import json
import os
import shutil

from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import settings
from src.core.embeddings import get_embeddings


def get_embedding_dimension() -> int:
    """Получить размерность эмбеддингов."""
    embeddings = get_embeddings()
    test_text = ["test"]
    embedding = embeddings.embed_documents(test_text)[0]
    return len(embedding)


def should_recreate_database(persist_dir: str, metadata_file: str) -> bool:
    """Проверить, нужно ли пересоздавать базу данных."""
    if not os.path.exists(persist_dir):
        return True

    current_dim = get_embedding_dimension()

    if os.path.exists(metadata_file):
        try:
            with open(metadata_file, encoding="utf-8") as f:
                saved_dim = json.load(f).get("embedding_dimension")
            if saved_dim == current_dim:
                print(f"Размерность совпадает ({current_dim}). Используем существующую базу.")
                return False
            else:
                print(f"Размерность изменилась: была {saved_dim}, стала {current_dim}. Пересоздаём базу.")
                return True
        except (json.JSONDecodeError, OSError) as e:
            print(f"Ошибка чтения метаданных: {e}. Пересоздаём базу.")
            return True
    else:
        print("Файл метаданных не найден. Пересоздаём базу.")
        return True


def load_documents(data_dir: str) -> list:
    """Загрузить документы из директории."""
    loader = DirectoryLoader(
        data_dir,
        glob="*.txt",
        loader_kwargs={"encoding": "utf-8"},
        loader_cls=TextLoader,
    )
    documents = loader.load()
    return documents


def split_documents(documents: list) -> list:
    """Разделить документы на чанки."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""],
        length_function=len,
    )
    return text_splitter.split_documents(documents)


def get_vectorstore() -> Chroma:
    """Получить или создать векторное хранилище."""
    persist_dir = settings.chroma_persist_dir
    metadata_file = os.path.join(persist_dir, "embedding_size.json")

    if should_recreate_database(persist_dir, metadata_file):
        if os.path.exists(persist_dir):
            shutil.rmtree(persist_dir)
            print(f"Удалена старая база: {persist_dir}")

        # Загрузка и индексация документов
        documents = load_documents(settings.data_dir)
        chunks = split_documents(documents)
        embeddings = get_embeddings()

        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=persist_dir,
        )

        # Сохранение размерности эмбеддингов
        os.makedirs(persist_dir, exist_ok=True)
        embedding_dim = get_embedding_dimension()
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump({"embedding_dimension": embedding_dim}, f)
        print(f"Сохранена размерность эмбеддингов: {embedding_dim}")
    else:
        embeddings = get_embeddings()
        vectorstore = Chroma(
            persist_directory=persist_dir,
            embedding_function=embeddings,
        )

    return vectorstore
