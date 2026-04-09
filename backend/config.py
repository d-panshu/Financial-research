import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    SERPAPI_KEY: str = os.getenv("SERPAPI_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/research.db")
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")
    CHECKPOINT_DB: str = os.getenv("CHECKPOINT_DB", "./data/checkpoints.db")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama3")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "llama3")
    MAX_ITERATIONS: int = int(os.getenv("MAX_ITERATIONS", "3"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")


settings = Settings()
