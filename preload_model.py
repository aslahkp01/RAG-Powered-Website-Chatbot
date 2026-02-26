"""Pre-download the embedding model so it is cached on disk.

Run this during the Render build step so the model is already present
when the server starts, avoiding a 5-10 min download on every cold start.
"""

from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

if __name__ == "__main__":
    print(f"Pre-downloading embedding model: {MODEL_NAME} ...")
    SentenceTransformer(MODEL_NAME)
    print("Model cached successfully.")
