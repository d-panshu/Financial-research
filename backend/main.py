from agents import load_agents
from graph.graph_builder import build_graph

from config import settings
print(settings.LLM_MODEL)

def main():
    print("🚀 Starting the application...")


    load_agents()


    graph = build_graph()

    print("✅ Application setup complete!")


if __name__ == "__main__":    main()