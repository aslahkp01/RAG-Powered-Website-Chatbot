from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from .config import Config


def build_vector_store(documents):
    if not documents:
        raise ValueError("No documents to process.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=Config.CHUNK_OVERLAP,
    )

    split_docs = splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(
        model_name=Config.EMBEDDING_MODEL
    )

    vector_store = FAISS.from_documents(split_docs, embeddings)

    return vector_store, len(split_docs)
