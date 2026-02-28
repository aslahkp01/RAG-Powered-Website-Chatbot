import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

_BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    USER_AGENT = "Mozilla/5.0"

    CRAWL_TIMEOUT = 15

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    MAX_DEPTH = 1
    MAX_PAGES = 5
    MAX_TEXT_PER_PAGE = 5000      # truncate each page's extracted text
    MAX_CHUNKS = 100               # hard cap on total chunks per session

    CHUNK_SIZE = 300
    CHUNK_OVERLAP = 100

    CRAWL_TIMEOUT = 15

    CORS_ORIGINS = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,https://rag-powered-website-chatbot.vercel.app",
    ).split(",")

    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    LLM_MODEL = "llama-3.1-8b-instant"

    # ── Paths ──────────────────────────────────────────────
    DATA_DIR = str(_BASE_DIR / "data" / "vectorstores")
