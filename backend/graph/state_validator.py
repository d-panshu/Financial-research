from graph.state import ResearchState


def validate_state(state: ResearchState):
    assert isinstance(state["query"], str)
    assert isinstance(state["ticker"], str)

    assert isinstance(state["news_articles"], list)
    assert state["news_status"] in ["pending", "done", "error"]

    assert isinstance(state["sec_chunks"], list)
    assert isinstance(state["sec_summary"], str)

    assert -1.0 <= state["sentiment_score"] <= 1.0

    if state["iteration_count"] > 3:
        raise Exception("❌ Max iteration limit exceeded")

    return True