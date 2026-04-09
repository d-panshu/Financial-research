import pytest
from unittest.mock import patch, MagicMock
import json


@pytest.fixture
def mock_all_llm_and_apis():
    """Patch all external calls so the full graph runs without real services."""
    sentiment_response = json.dumps({"score": 0.6, "rationale": "Positive outlook based on news."})

    with (
        patch("backend.agents.news_fetcher.GoogleSearch") as mock_search,
        patch("backend.agents.sec_analyzer.OllamaLLM") as mock_sec_llm,
        patch("backend.agents.sec_analyzer.query_sec") as mock_retriever,
        patch("backend.agents.sentiment_scorer.OllamaLLM") as mock_sent_llm,
        patch("backend.agents.portfolio_synthesizer.OllamaLLM") as mock_synth_llm,
        patch("backend.agents.portfolio_synthesizer._generate_pdf") as mock_pdf,
    ):
        mock_search.return_value.get_dict.return_value = {
            "news_results": [{"title": "AAPL up 5%", "snippet": "Record quarter", "date": "2024-01-01", "source": "Reuters"}]
        }
        mock_retriever.return_value = ["Revenue: $90B in Q4", "Net income grew 12% YoY"]
        mock_sec_llm.return_value.invoke.return_value = "Strong revenue growth in Q4 2024."
        mock_sent_llm.return_value.invoke.return_value = sentiment_response
        mock_synth_llm.return_value.invoke.return_value = "Executive Summary: AAPL is a strong buy."
        mock_pdf.return_value = "./data/reports/AAPL_test.pdf"
        yield


def test_full_pipeline_runs_to_hitl_pause(mock_all_llm_and_apis):
    from backend.graph.graph_builder import build_graph
    from backend.graph.state import default_state

    graph = build_graph()
    config = {"configurable": {"thread_id": "AAPL_integration_test"}}
    state = default_state("Should we invest in Apple?", "AAPL")

    events = list(graph.stream(state, config=config))
    assert len(events) > 0

    # Graph should pause before human_review — not reach portfolio_synthesizer yet
    node_names = [list(e.keys())[0] for e in events]
    assert "news_fetcher" in node_names
    assert "portfolio_synthesizer" not in node_names


def test_full_pipeline_completes_after_approval(mock_all_llm_and_apis):
    from backend.graph.graph_builder import build_graph
    from backend.graph.state import default_state

    graph = build_graph()
    config = {"configurable": {"thread_id": "AAPL_approval_test"}}
    state = default_state("Should we invest in Apple?", "AAPL")

    # Run to HITL pause
    for _ in graph.stream(state, config=config):
        pass

    # Simulate human approval
    graph.update_state(config, {"human_approved": True, "human_feedback": "Looks good"})

    # Resume
    final_events = list(graph.stream(None, config=config))
    final_state = graph.get_state(config).values

    assert final_state.get("final_report") is not None
    assert final_state.get("error") is None


def test_pipeline_restarts_after_rejection(mock_all_llm_and_apis):
    from backend.graph.graph_builder import build_graph
    from backend.graph.state import default_state

    graph = build_graph()
    config = {"configurable": {"thread_id": "AAPL_reject_test"}}
    state = default_state("Should we invest in Apple?", "AAPL")

    for _ in graph.stream(state, config=config):
        pass

    graph.update_state(config, {
        "human_approved": False,
        "human_feedback": "Need more data on Q4 guidance",
    })

    rerun_events = list(graph.stream(None, config=config))
    rerun_nodes = [list(e.keys())[0] for e in rerun_events]

    # Graph restarts from news_fetcher after rejection
    assert "news_fetcher" in rerun_nodes
