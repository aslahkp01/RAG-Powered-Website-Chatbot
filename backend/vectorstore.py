import os

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings

from .config import Config

_embeddings = None


def _get_embeddings():
    """Return (and lazily initialise) the shared embedding model."""
    global _embeddings
    if _embeddings is None:
        _embeddings = FastEmbedEmbeddings(
            model_name=Config.EMBEDDING_MODEL,
            cache_dir=Config.MODEL_CACHE_DIR,
        )
    return _embeddings


# ── Build ────────────────────────────────────────────────────

def build_vector_store(documents):
    if not documents:
        raise ValueError("No documents to process.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=Config.CHUNK_OVERLAP,
    )

    split_docs = splitter.split_documents(documents)
    vector_store = FAISS.from_documents(split_docs, _get_embeddings())
    return vector_store, len(split_docs)


# ── Disk persistence ─────────────────────────────────────────

def save_vector_store(vector_store, session_id):
    """Persist a FAISS index to *DATA_DIR/<session_id>*."""
    path = os.path.join(Config.DATA_DIR, session_id)
    os.makedirs(path, exist_ok=True)
    vector_store.save_local(path)


def load_vector_store(session_id):
    """Load a FAISS index from disk.  Returns *None* if missing."""
    path = os.path.join(Config.DATA_DIR, session_id)
    if not os.path.isdir(path):
        return None
    return FAISS.load_local(
        path, _get_embeddings(), allow_dangerous_deserialization=True
    )


def list_persisted_sessions():
    """Return session-id list for every index stored on disk."""
    if not os.path.isdir(Config.DATA_DIR):
        return []
    return [
        d for d in os.listdir(Config.DATA_DIR)
        if os.path.isdir(os.path.join(Config.DATA_DIR, d))
    ]
