import logging
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings

from backend.config import settings

logger = logging.getLogger(__name__)

_vectorstore_cache: dict[str, Chroma] = {}


def _get_vectorstore(ticker: str) -> Chroma:
    key = ticker.lower()
    if key not in _vectorstore_cache:
        embeddings = OllamaEmbeddings(
            model=settings.EMBEDDING_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
        )
        _vectorstore_cache[key] = Chroma(
            persist_directory=settings.CHROMA_PERSIST_DIR,
            embedding_function=embeddings,
            collection_name=f"sec_{key}",
        )
    return _vectorstore_cache[key]


def query_sec(ticker: str, question: str, k: int = 5) -> list[str]:
    logger.info("Querying SEC vector store for ticker: %s, k=%d", ticker, k)
    try:
        vectorstore = _get_vectorstore(ticker)
        results = vectorstore.similarity_search_with_score(
            question,
            k=k,
            filter={"ticker": ticker.upper()},
        )
        chunks = [doc.page_content for doc, _score in results]
        logger.info("Retrieved %d chunks for ticker: %s", len(chunks), ticker)
        return chunks
    except Exception as e:
        logger.error("SEC retrieval failed for ticker %s: %s", ticker, str(e))
        return []
