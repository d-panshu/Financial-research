import logging
import argparse
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama import OllamaEmbeddings

from backend.config import settings

logger = logging.getLogger(__name__)


def ingest_sec_filing(pdf_path: str, ticker: str) -> int:
    logger.info("Ingesting SEC filing: %s for ticker: %s", pdf_path, ticker)

    loader = PyPDFLoader(pdf_path)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " "],
    )
    chunks = splitter.split_documents(docs)

    for chunk in chunks:
        chunk.metadata["ticker"] = ticker.upper()
        chunk.metadata["source"] = "sec_filing"

    embeddings = OllamaEmbeddings(
        model=settings.EMBEDDING_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
    )

    vectorstore = Chroma.from_documents(
        chunks,
        embeddings,
        persist_directory=settings.CHROMA_PERSIST_DIR,
        collection_name=f"sec_{ticker.lower()}",
    )
    vectorstore.persist()

    logger.info("Ingested %d chunks for ticker: %s", len(chunks), ticker)
    return len(chunks)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest SEC filing PDF into ChromaDB")
    parser.add_argument("--pdf", required=True, help="Path to the SEC filing PDF")
    parser.add_argument("--ticker", required=True, help="Stock ticker symbol")
    args = parser.parse_args()

    count = ingest_sec_filing(args.pdf, args.ticker)
    print(f"Successfully ingested {count} chunks for {args.ticker}")
