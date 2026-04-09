import json
import logging
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate

from backend.graph.state import ResearchState
from backend.config import settings

logger = logging.getLogger(__name__)

SENTIMENT_PROMPT = PromptTemplate.from_template(
    "You are a financial sentiment analyst.\n"
    "Ticker: {ticker}\n\n"
    "Recent News:\n{news}\n\n"
    "SEC Filing Summary:\n{sec}\n\n"
    "Analyse the overall investment sentiment for {ticker}.\n"
    "Return ONLY valid JSON with this exact schema:\n"
    '{{"score": <float between -1.0 and 1.0>, "rationale": "<2-3 sentence explanation>"}}\n'
    "score -1.0 = strongly bearish, 0.0 = neutral, 1.0 = strongly bullish."
)


def sentiment_scorer_node(state: ResearchState) -> dict:
    ticker = state["ticker"]
    logger.info("Scoring sentiment for ticker: %s", ticker)

    try:
        llm = OllamaLLM(model=settings.LLM_MODEL, format="json")

        news_text = "\n".join(
            f"- {a['title']}: {a['snippet']}"
            for a in state.get("news_articles", [])[:3]
        )

        raw = llm.invoke(SENTIMENT_PROMPT.format(
            ticker=ticker,
            news=news_text or "No news available.",
            sec=state.get("sec_summary", "No SEC data.")[:600],
        ))

        data = json.loads(raw)
        score = float(data.get("score", 0.0))
        score = max(-1.0, min(1.0, score))

        return {
            "sentiment_score": score,
            "sentiment_rationale": data.get("rationale", ""),
            "sentiment_status": "done",
        }

    except json.JSONDecodeError as e:
        logger.error("Sentiment JSON parse failed for %s: %s", ticker, str(e))
        return {"sentiment_score": 0.0, "sentiment_rationale": "Parse error", "sentiment_status": "error"}
    except Exception as e:
        logger.error("Sentiment scoring failed for %s: %s", ticker, str(e))
        return {"sentiment_status": "error", "error": f"Sentiment scorer: {str(e)}"}
