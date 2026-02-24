import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    USER_AGENT = "Mozilla/5.0"

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    MAX_DEPTH = 1
    MAX_PAGES = 10

    CHUNK_SIZE = 800
    CHUNK_OVERLAP = 100

    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")

    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    LLM_MODEL = "llama-3.1-8b-instant"
