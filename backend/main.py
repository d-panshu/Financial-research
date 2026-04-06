from agents import load_agents
from graph.graph_builder import build_graph
from graph.state_factory import create_initial_state
from graph.state_validator import validate_state

from config import settings
print(settings.LLM_MODEL)

def main():
    print("🚀 Starting the application...")


    load_agents()


    graph = build_graph()

    state = create_initial_state(
        query="What is the market cap of apple?",
        ticker="AAPL"
    )

    validate_state(state)

    print("✅ State is valid. Ready to run the graph with agents!")
    print("✅ Application setup complete!")


if __name__ == "__main__":    main()