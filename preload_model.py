"""Pre-download the embedding model during the Render build step.

The model is downloaded fresh on the Linux build environment so there
are no Windows → Linux cache mismatches.  The downloaded model stays
in the build cache between deploys.
"""

from fastembed import TextEmbedding

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

if __name__ == "__main__":
    print(f"Pre-downloading embedding model: {MODEL_NAME}")
    TextEmbedding(model_name=MODEL_NAME)
    print("Model cached successfully.")
