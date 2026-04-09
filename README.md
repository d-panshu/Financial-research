# Financial Research System

A production-grade multi-agent AI system for financial research. Uses LangGraph to orchestrate 4 specialised agents (News Fetcher, SEC Analyzer, Sentiment Scorer, Portfolio Synthesizer) with a Human-in-the-Loop checkpoint before any report is finalised.

## Architecture

```
News Fetcher → SEC Analyzer → Sentiment Scorer → Aggregator
                                                      ↓
                                              [HITL Checkpoint]
                                               ↙           ↘
                                         Approved        Rejected
                                              ↓               ↓
                                      Portfolio         News Fetcher
                                      Synthesizer       (re-run)
```

**Tech Stack**

| Layer | Technology |
|---|---|
| Orchestration | LangGraph (StateGraph + SqliteSaver checkpointer) |
| Agent Framework | LangChain + LangChain-Ollama |
| Vector Store | ChromaDB (local) / Pinecone (prod) |
| LLM | Ollama + Llama 3 (local) or GPT-4o (cloud) |
| Backend API | FastAPI + WebSockets |
| Frontend | React 18 + React Flow + Tailwind CSS |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Real-time Search | SerpAPI Google News |
| PDF Reports | ReportLab |

## Prerequisites

- Python 3.12+
- Node.js 20+
- [Ollama](https://ollama.com) running locally
- SerpAPI key (for news)

## Quick Start

**1. Clone and set up environment**

```bash
git clone <repo>
cd financial-research-system

cp .env.example .env
# Edit .env — add your SERPAPI_KEY at minimum
```

**2. Backend**

```bash
cd backend
python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Pull and start the LLM
ollama pull llama3
ollama serve
```

**3. Ingest an SEC filing** (optional but needed for SEC Analyzer)

```bash
python -m backend.rag.ingest --pdf ./data/sec_filings/AAPL_10K.pdf --ticker AAPL
```

**4. Start the backend**

```bash
python backend/main.py
# API runs at http://localhost:8000
```

**5. Frontend**

```bash
cd frontend
npm install
npm run dev
# Dashboard at http://localhost:5173
```

## Docker (Production)

```bash
docker-compose up --build
```

Update `DATABASE_URL` in `.env` to `postgresql://research:research@postgres:5432/financial_research` before running with Docker.

## Usage

1. Open `http://localhost:5173`
2. Enter a ticker (e.g. `AAPL`) and a research question
3. Watch agents execute in real-time on the graph
4. Review the aggregated context when the Human Review panel appears
5. Approve (generates PDF report) or Reject (re-runs all agents)
6. Download the PDF report

## Key Commands

```bash
# Run tests
pytest tests/ -v

# Ingest SEC filing
python -m backend.rag.ingest --pdf ./data/sec_filings/TSLA_10K.pdf --ticker TSLA

# Test SEC retrieval
python -c "from backend.rag.retriever import query_sec; print(query_sec('AAPL', 'revenue'))"

# View LangGraph as Mermaid
python -c "from backend.graph.graph_builder import build_graph; print(build_graph().get_graph().draw_mermaid())"

# Inspect checkpoints
sqlite3 ./data/checkpoints.db 'SELECT * FROM checkpoints LIMIT 5;'

# Test WebSocket
wscat -c ws://localhost:8000/ws/research
```

## Project Structure

```
financial-research-system/
├── backend/
│   ├── agents/              # Pure function agents: (state) → dict
│   │   ├── news_fetcher.py
│   │   ├── sec_analyzer.py
│   │   ├── sentiment_scorer.py
│   │   └── portfolio_synthesizer.py
│   ├── graph/               # LangGraph wiring — separate from agent logic
│   │   ├── state.py         # ResearchState TypedDict
│   │   ├── graph_builder.py # Nodes, edges, HITL checkpoint
│   │   └── conditions.py    # Conditional routing functions
│   ├── rag/                 # Standalone RAG pipeline
│   │   ├── ingest.py        # PDF → chunks → ChromaDB
│   │   └── retriever.py     # query_sec() with caching
│   ├── api/
│   │   ├── server.py        # FastAPI app + CORS + lifespan
│   │   ├── models.py        # Pydantic schemas
│   │   └── routes/
│   │       ├── research.py  # POST /research, WS /ws/research
│   │       ├── hitl.py      # POST /api/approve|reject
│   │       └── report.py    # GET /api/report/{session_id}
│   ├── db/
│   │   ├── database.py      # SQLAlchemy engine + session
│   │   ├── models.py        # ResearchSession ORM
│   │   └── migrations/      # Alembic
│   ├── config.py            # All env vars in one place
│   ├── requirements.txt
│   └── main.py
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── AgentGraph.jsx    # React Flow live execution graph
│       │   ├── HumanReview.jsx   # Approve/Reject panel
│       │   ├── ReportViewer.jsx  # Final report + PDF download
│       │   ├── EventLog.jsx      # Live WebSocket event feed
│       │   └── StatusBadge.jsx
│       ├── hooks/
│       │   └── useWebSocket.js   # WebSocket state management
│       └── pages/
│           └── Dashboard.jsx     # Main page
├── tests/
│   ├── test_state.py
│   ├── test_agents.py       # Agent unit tests with mocks
│   ├── test_integration.py  # Full pipeline tests
│   └── test_api.py
├── docker-compose.yml
├── alembic.ini
├── pytest.ini
└── .env.example
```

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `SERPAPI_KEY` | SerpAPI key for news search | required |
| `OPENAI_API_KEY` | OpenAI key (if not using Ollama) | optional |
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434` |
| `LLM_MODEL` | Model name for Ollama or OpenAI | `llama3` |
| `DATABASE_URL` | SQLAlchemy DB URL | SQLite |
| `MAX_ITERATIONS` | HITL reject loop guard | `3` |

## Switching to GPT-4o

```bash
# In .env
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4o
```

Then replace `OllamaLLM` with `ChatOpenAI` in each agent file.


