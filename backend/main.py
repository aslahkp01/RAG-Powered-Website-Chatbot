import threading
import uuid
from typing import Dict, List, Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl

from .crawler import crawl
from .config import Config
from .llm import generate_answer
from .retriever import retrieve_documents
from .vectorstore import build_vector_store, _get_embeddings

app = FastAPI(title="RAG Web Scraper API", version="1.0.0")


@app.on_event("startup")
def preload_models():
    """Load the embedding model in a background thread so the port binds immediately."""
    threading.Thread(target=_get_embeddings, daemon=True).start()


app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?|https://rag-powered-website-chatbot\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class IndexRequest(BaseModel):
    url: HttpUrl


class IndexResponse(BaseModel):
    session_id: str
    pages_crawled: int
    chunks_created: int


class ChatRequest(BaseModel):
    session_id: str
    question: str


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatResponse(BaseModel):
    answer: str
    history: List[Message]


class SessionData(BaseModel):
    url: str
    history: List[Message]


_vectorstores: Dict[str, object] = {}
_sessions: Dict[str, SessionData] = {}
_state_lock = threading.Lock()


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/index", response_model=IndexResponse)
def index_site(payload: IndexRequest) -> IndexResponse:
    documents = crawl(str(payload.url))

    if not documents:
        raise HTTPException(status_code=400, detail="No content could be extracted from this website.")

    vector_store, chunk_count = build_vector_store(documents)

    session_id = str(uuid.uuid4())
    with _state_lock:
        _vectorstores[session_id] = vector_store
        _sessions[session_id] = SessionData(url=str(payload.url), history=[])

    return IndexResponse(
        session_id=session_id,
        pages_crawled=len(documents),
        chunks_created=chunk_count,
    )


@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    with _state_lock:
        vector_store = _vectorstores.get(payload.session_id)
        session = _sessions.get(payload.session_id)

    if vector_store is None or session is None:
        raise HTTPException(status_code=404, detail="Session not found. Index a website first.")

    docs = retrieve_documents(vector_store, question)
    context = "\n\n".join([doc.page_content for doc in docs])
    answer = generate_answer(question, context)

    user_message = Message(role="user", content=question)
    assistant_message = Message(role="assistant", content=answer)

    with _state_lock:
        session.history.append(user_message)
        session.history.append(assistant_message)

    return ChatResponse(answer=answer, history=session.history)
