"""Pre-download the embedding model into model_cache/.

Run locally *before* pushing so the cached ONNX model is already
present in the repo — no heavy download needed on Render.

Usage
-----
    python preload_model.py          # download once
    git add model_cache/             # commit the cache
    git push                         # deploy includes the model
"""

from pathlib import Path
from fastembed import TextEmbedding

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
CACHE_DIR = str(Path(__file__).resolve().parent / "model_cache")

if __name__ == "__main__":
    print(f"Pre-downloading embedding model: {MODEL_NAME}")
    print(f"Cache directory: {CACHE_DIR}")
    TextEmbedding(model_name=MODEL_NAME, cache_dir=CACHE_DIR)
    print("\nModel cached successfully.")
    print("Now commit model_cache/ to your repo and push.")
