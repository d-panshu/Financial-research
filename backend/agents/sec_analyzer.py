import logging
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate

from backend.graph.state import ResearchState
from backend.rag.retriever import query_sec
from backend.config import settings

logger = logging.getLogger(__name__)

CONFIDENCE_THRESHOLD = 0.6

SEC_PROMPT = PromptTemplate.from_template(
    "You are a financial analyst reviewing SEC filings.\n"
    "Ticker: {ticker}\n"
    "Question: {query}\n\n"
    "Relevant filing excerpts:\n{context}\n\n"
    "Provide a concise summary (3-5 sentences) of the key financial information. "
    "Focus on revenue, risks, and forward guidance."
)


def _compute_confidence(chunks: list[str]) -> float:
    if not chunks:
        return 0.0
    avg_len = sum(len(c) for c in chunks) / len(chunks)
    return min(1.0, avg_len / 500)


def sec_analyzer_node(state: ResearchState) -> dict:
    ticker = state["ticker"]
    query = state["query"]
    logger.info("Analyzing SEC filings for ticker: %s", ticker)

    try:
        chunks = query_sec(ticker, query, k=5)

        # Corrective RAG: re-query with broader question if confidence is low
        confidence = _compute_confidence(chunks)
        if confidence < CONFIDENCE_THRESHOLD:
            logger.warning("Low confidence (%.2f) — re-querying SEC for %s", confidence, ticker)
            broader_chunks = query_sec(ticker, f"{ticker} annual revenue profit loss risk", k=8)
            chunks = broader_chunks or chunks

        if not chunks:
            return {
                "sec_chunks": [],
                "sec_summary": "No SEC filing data available for this ticker.",
                "sec_status": "done",
            }

        llm = OllamaLLM(model=settings.LLM_MODEL)
        context = "\n---\n".join(chunks[:5])
        summary = llm.invoke(SEC_PROMPT.format(
            ticker=ticker,
            query=query,
            context=context,
        ))

        return {
            "sec_chunks": chunks,
            "sec_summary": summary,
            "sec_status": "done",
        }

    except Exception as e:
        logger.error("SEC analysis failed for %s: %s", ticker, str(e))
        return {"sec_status": "error", "error": f"SEC analyzer: {str(e)}"}
