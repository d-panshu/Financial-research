import os
import logging
from serpapi import GoogleSearch
from backend.graph.state import ResearchState

logger = logging.getLogger(__name__)


def news_fetcher_node(state: ResearchState) -> dict:
    ticker = state["ticker"]
    logger.info("Fetching news for ticker: %s", ticker)

    try:
        search = GoogleSearch({
            "q": f"{ticker} stock news earnings",
            "tbm": "nws",
            "num": 10,
            "api_key": os.getenv("SERPAPI_KEY"),
        })
        results = search.get_dict().get("news_results", [])
        articles = [
            {
                "title": r.get("title", ""),
                "snippet": r.get("snippet", ""),
                "date": r.get("date"),
                "source": r.get("source"),
                "link": r.get("link"),
            }
            for r in results[:5]
        ]
        logger.info("Fetched %d articles for %s", len(articles), ticker)
        return {"news_articles": articles, "news_status": "done"}

    except Exception as e:
        logger.error("News fetch failed for %s: %s", ticker, str(e))
        return {"news_status": "error", "error": f"News fetcher: {str(e)}"}
