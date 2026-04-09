import pytest
from unittest.mock import patch, MagicMock
from backend.graph.state import default_state


def make_state(**overrides):
    s = default_state("Should I buy Apple?", "AAPL")
    s.update(overrides)
    return s


class TestNewsFetcher:
    @patch("backend.agents.news_fetcher.GoogleSearch")
    def test_success(self, mock_search_cls):
        mock_search = MagicMock()
        mock_search.get_dict.return_value = {
            "news_results": [
                {"title": "Apple Hits Record High", "snippet": "AAPL surged...", "date": "2024-01-01", "source": "Bloomberg"}
            ]
        }
        mock_search_cls.return_value = mock_search

        from backend.agents.news_fetcher import news_fetcher_node
        result = news_fetcher_node(make_state())

        assert result["news_status"] == "done"
        assert len(result["news_articles"]) == 1
        assert result["news_articles"][0]["title"] == "Apple Hits Record High"

    @patch("backend.agents.news_fetcher.GoogleSearch")
    def test_api_error_returns_error_status(self, mock_search_cls):
        mock_search_cls.side_effect = Exception("API quota exceeded")

        from backend.agents.news_fetcher import news_fetcher_node
        result = news_fetcher_node(make_state())

        assert result["news_status"] == "error"
        assert "error" in result


class TestSentimentScorer:
    @patch("backend.agents.sentiment_scorer.OllamaLLM")
    def test_valid_json_response(self, mock_llm_cls):
        import json
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = json.dumps({"score": 0.75, "rationale": "Strong earnings beat."})
        mock_llm_cls.return_value = mock_llm

        from backend.agents.sentiment_scorer import sentiment_scorer_node
        state = make_state(
            news_articles=[{"title": "AAPL up", "snippet": "beats earnings"}],
            sec_summary="Revenue up 10%",
        )
        result = sentiment_scorer_node(state)

        assert result["sentiment_status"] == "done"
        assert result["sentiment_score"] == 0.75
        assert "Strong" in result["sentiment_rationale"]

    @patch("backend.agents.sentiment_scorer.OllamaLLM")
    def test_score_clamped_to_range(self, mock_llm_cls):
        import json
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = json.dumps({"score": 99.9, "rationale": "extreme"})
        mock_llm_cls.return_value = mock_llm

        from backend.agents.sentiment_scorer import sentiment_scorer_node
        result = sentiment_scorer_node(make_state(news_articles=[], sec_summary=""))

        assert result["sentiment_score"] <= 1.0

    @patch("backend.agents.sentiment_scorer.OllamaLLM")
    def test_invalid_json_returns_error_status(self, mock_llm_cls):
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = "this is not json"
        mock_llm_cls.return_value = mock_llm

        from backend.agents.sentiment_scorer import sentiment_scorer_node
        result = sentiment_scorer_node(make_state(news_articles=[], sec_summary=""))

        assert result["sentiment_status"] == "error"


class TestConditions:
    def test_should_review_routes_to_human(self):
        from backend.graph.conditions import should_review
        state = make_state(iteration_count=0)
        assert should_review(state) == "human_review"

    def test_should_review_routes_to_synthesizer_at_max_iterations(self):
        from backend.graph.conditions import should_review
        state = make_state(iteration_count=3)
        assert should_review(state) == "synthesizer"

    def test_should_review_routes_to_end_on_error(self):
        from backend.graph.conditions import should_review
        state = make_state(error="Something failed", iteration_count=0)
        assert should_review(state) == "end"

    def test_route_after_human_approved(self):
        from backend.graph.conditions import route_after_human
        state = make_state(human_approved=True)
        assert route_after_human(state) == "approved"

    def test_route_after_human_rejected(self):
        from backend.graph.conditions import route_after_human
        state = make_state(human_approved=False)
        assert route_after_human(state) == "rejected"

    def test_route_after_human_none_returns_end(self):
        from backend.graph.conditions import route_after_human
        state = make_state(human_approved=None)
        assert route_after_human(state) == "end"
