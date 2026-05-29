"""ChromaDB vector store for the RAG pipeline (Week 4 · Day 3).

Stores chunk embeddings + metadata and powers semantic search:

    PDF -> Chunks -> Embeddings -> Vector DB -> (semantic search)

The store persists to ``backend/uploads/vectorstore/`` (gitignored) so indexed
documents survive restarts.
"""

from __future__ import annotations

from pathlib import Path

from app.rag.embeddings import MODEL_NAME, get_embedder

# backend/app/rag/vector_store.py -> parents[2] == backend/
BACKEND_DIR = Path(__file__).resolve().parents[2]
VECTORSTORE_DIR = BACKEND_DIR / "uploads" / "vectorstore"
COLLECTION_NAME = "documents"


class VectorStore:
    def __init__(self) -> None:
        import chromadb

        VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(VECTORSTORE_DIR))
        # Cosine space matches our normalized embeddings.
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    def add_chunks(self, document_id: str, filename: str, chunks: list) -> int:
        """Embed and index a document's chunks. Returns number indexed."""
        if not chunks:
            return 0
        embedder = get_embedder()
        texts = [c.text for c in chunks]
        embeddings = embedder.embed(texts)
        self.collection.add(
            ids=[c.chunk_id for c in chunks],
            documents=texts,
            embeddings=embeddings,
            metadatas=[
                {
                    "document_id": document_id,
                    "filename": filename,
                    "page": c.page if c.page is not None else 0,
                    "chunk_index": c.chunk_index,
                }
                for c in chunks
            ],
        )
        return len(chunks)

    def search(
        self,
        query: str,
        top_k: int = 5,
        document_id: str | None = None,
    ) -> list[dict]:
        """Semantic search: embed the query, return nearest chunks."""
        if self.collection.count() == 0:
            return []
        q_embedding = get_embedder().embed_one(query)
        where = {"document_id": document_id} if document_id else None
        res = self.collection.query(
            query_embeddings=[q_embedding],
            n_results=top_k,
            where=where,
        )

        results: list[dict] = []
        ids = res.get("ids", [[]])[0]
        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        dists = res.get("distances", [[]])[0]
        for cid, text, meta, dist in zip(ids, docs, metas, dists):
            # cosine distance -> similarity in [0, 1]
            similarity = max(0.0, 1.0 - float(dist))
            results.append(
                {
                    "chunk_id": cid,
                    "document_id": meta.get("document_id", ""),
                    "filename": meta.get("filename", ""),
                    "page": meta.get("page"),
                    "chunk_index": meta.get("chunk_index", 0),
                    "text": text,
                    "similarity": round(similarity, 4),
                }
            )
        return results

    def delete_document(self, document_id: str) -> None:
        self.collection.delete(where={"document_id": document_id})

    def count(self) -> int:
        return self.collection.count()

    @property
    def embedding_model(self) -> str:
        return MODEL_NAME


_store: VectorStore | None = None


def get_vector_store() -> VectorStore:
    """Lazily-loaded singleton vector store."""
    global _store
    if _store is None:
        _store = VectorStore()
    return _store
