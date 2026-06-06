"""Embedding helpers — course-provided. DO NOT modify.

Wraps sentence-transformers `all-MiniLM-L6-v2` (384-dim, cosine-friendly),
the same model used in the Module 8 Lab so the vector primitive carries
forward across engines (Weaviate -> Neo4j).
"""

from __future__ import annotations

from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384


def get_embedder() -> SentenceTransformer:
    """Load and return a SentenceTransformer instance.

    On first call the model downloads from the HuggingFace hub (~90 MB).
    Subsequent calls in the same process reuse the loaded model; subsequent
    runs reuse the on-disk cache at ~/.cache/huggingface.
    """
    return SentenceTransformer(MODEL_NAME)


def embed_text(embedder: SentenceTransformer, text: str) -> list[float]:
    """Encode a single string to a 384-dim Python list of floats.

    Neo4j's vector index expects a list, not a numpy array — we convert
    explicitly so callers don't have to remember.
    """
    vec = embedder.encode(text, show_progress_bar=False, convert_to_numpy=True)
    return [float(x) for x in vec.tolist()]
