"""RAG сервис для обработки запросов."""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough

from src.core.llm import get_llm
from src.core.vectorstore import get_vectorstore
from src.schemas.query import QueryRequest, QueryResponse, SourceDocument

PROMPT_TEMPLATE = """
Используй следующий контекст для ответа на вопрос.
Если в контексте нет информации для ответа — скажи, что не знаешь.

Контекст:
{context}

Вопрос:
{question}

Ответ:
"""


def format_docs(docs: list) -> str:
    """Форматировать документы в строку."""
    return "\n\n".join(doc.page_content for doc in docs)


class RAGService:
    """Сервис для RAG-запросов."""

    def __init__(self):
        self.vectorstore = get_vectorstore()
        self.llm = get_llm()
        self._rag_chain = None

    def _get_rag_chain(self, top_k: int):
        """Получить RAG цепочку."""
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": top_k})

        prompt = PromptTemplate.from_template(PROMPT_TEMPLATE)

        return (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )

    def query(self, request: QueryRequest) -> QueryResponse:
        """Обработать запрос."""
        rag_chain = self._get_rag_chain(request.top_k)
        answer = rag_chain.invoke(request.question)

        # Получение источников
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": request.top_k})
        docs = retriever.invoke(request.question)
        sources = [
            SourceDocument(content=doc.page_content, metadata=doc.metadata)
            for doc in docs
        ]

        return QueryResponse(answer=answer, sources=sources)


# Глобальный экземпляр сервиса
rag_service = RAGService()
