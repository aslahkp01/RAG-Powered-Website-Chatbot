import json
import os
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
from .vectorstore import (
    build_vector_store,
    save_vector_store,
    load_vector_store,
    list_persisted_sessions,
    _get_embeddings,
)

app = FastAPI(title="RAG Web Scraper API", version="1.0.0")


# ── Pydantic models ──────────────────────────────────────────────


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


# ── In-memory caches (vector stores loaded on-demand) ────────────

_vectorstores: Dict[str, object] = {}
_sessions: Dict[str, SessionData] = {}
_state_lock = threading.Lock()


# ── Helpers: persist / restore sessions ──────────────────────────

def _meta_path(session_id: str) -> str:
    return os.path.join(Config.DATA_DIR, session_id, "meta.json")


def _persist_session(session_id: str) -> None:
    """Write session metadata alongside its FAISS index."""
    session = _sessions.get(session_id)
    if not session:
        return
    path = os.path.join(Config.DATA_DIR, session_id)
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, "meta.json"), "w") as f:
        json.dump(
            {"url": session.url, "history": [m.model_dump() for m in session.history]},
            f,
        )


def _restore_sessions() -> None:
    """Reload session metadata from disk (vector stores stay on disk until needed)."""
    for sid in list_persisted_sessions():
        mp = _meta_path(sid)
        if not os.path.isfile(mp):
            continue
        with open(mp) as f:
            meta = json.load(f)
        with _state_lock:
            if sid not in _sessions:
                _sessions[sid] = SessionData(
                    url=meta.get("url", ""),
                    history=[Message(**m) for m in meta.get("history", [])],
                )


def _get_or_load_vectorstore(session_id: str):
    """Return vector store from RAM cache, or load from disk."""
    vs = _vectorstores.get(session_id)
    if vs is not None:
        return vs
    vs = load_vector_store(session_id)
    if vs is not None:
        with _state_lock:
            _vectorstores[session_id] = vs
    return vs


# ── Startup ──────────────────────────────────────────────────────

@app.on_event("startup")
def startup():
    os.makedirs(Config.DATA_DIR, exist_ok=True)
    threading.Thread(target=_bootstrap, daemon=True).start()


def _bootstrap():
    _get_embeddings()       # warm-up embedding model
    _restore_sessions()     # reload metadata from disk


# ── CORS ─────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?|https://rag-powered-website-chatbot\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routes ───────────────────────────────────────────────────────

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

    # Persist vector store + metadata to disk
    save_vector_store(vector_store, session_id)
    _persist_session(session_id)

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
        session = _sessions.get(payload.session_id)

    vector_store = _get_or_load_vectorstore(payload.session_id)

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

    _persist_session(payload.session_id)

    return ChatResponse(answer=answer, history=session.history)
