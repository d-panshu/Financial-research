import os 
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SERPAPI_KEY = os.getenv("SERPAPI_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")

    DATABASE_URL = os.getenv("DATABASE_URL")
    CHROMA_DIR = os.getenv("CHROMA_PERSIST_DIR")
    CHECKPOINT_DB = os.getenv("CHECKPOINT_DB")

    LLM_MODEL = os.getenv("LLM_MODEL", "llama3")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "llama3")

settings = Settings()