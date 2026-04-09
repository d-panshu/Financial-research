import json
import pytest
from backend.graph.state import ResearchState, default_state


def test_default_state_structure():
    state = default_state("Should I buy Apple?", "AAPL")
    assert state["query"] == "Should I buy Apple?"
    assert state["ticker"] == "AAPL"
    assert state["news_articles"] == []
    assert state["iteration_count"] == 0
    assert state["human_approved"] is None
    assert state["final_report"] is None
    assert state["error"] is None


def test_state_json_serialisable():
    state = default_state("Test query", "TSLA")
    # Must serialise cleanly for SQLite checkpointer
    serialised = json.dumps(dict(state))
    loaded = json.loads(serialised)
    assert loaded["ticker"] == "TSLA"


def test_state_all_optional_fields_default_none():
    state = default_state("q", "X")
    optional_fields = ["human_approved", "human_feedback", "final_report", "error"]
    for field in optional_fields:
        assert state[field] is None, f"Field {field} should default to None"
