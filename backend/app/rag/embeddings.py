"""Embedding model wrapper for the RAG pipeline (Week 4 · Day 3).

Turns text into vectors using SentenceTransformers ``all-MiniLM-L6-v2``
(384 dims, small + fast + local). Embeddings are L2-normalized so cosine
similarity works cleanly in the vector store.
"""

from __future__ import annotations

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384


class Embedder:
    def __init__(self, model_name: str = MODEL_NAME) -> None:
        # Imported lazily so the backend can boot even if the heavy ML deps
        # aren't installed in a given environment.
        from sentence_transformers import SentenceTransformer

        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of texts -> list of vectors."""
        vectors = self.model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        return vectors.tolist()

    def embed_one(self, text: str) -> list[float]:
        return self.embed([text])[0]


_embedder: Embedder | None = None


def get_embedder() -> Embedder:
    """Lazily-loaded singleton (model loads once per process)."""
    global _embedder
    if _embedder is None:
        _embedder = Embedder()
    return _embedder
