import pytest
import os

os.environ.setdefault("SERPAPI_KEY", "test_key")
os.environ.setdefault("DATABASE_URL", "sqlite:///./data/test_research.db")
os.environ.setdefault("CHROMA_PERSIST_DIR", "./data/test_chroma")
os.environ.setdefault("CHECKPOINT_DB", "./data/test_checkpoints.db")
os.environ.setdefault("LLM_MODEL", "llama3")
os.environ.setdefault("EMBEDDING_MODEL", "llama3")
os.environ.setdefault("MAX_ITERATIONS", "3")
