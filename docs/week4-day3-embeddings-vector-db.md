# Week 4 · Day 3 — Embeddings + Vector Database

**Goal:** Convert uploaded notes into a *searchable AI memory* so a student can ask
*"Explain recursion"* and the AI automatically finds the related lecture content.

---

## The pipeline

```
PDF  ──►  Chunks  ──►  Embeddings  ──►  Vector DB  ──►  Semantic Search
       (Day 2)      all-MiniLM-L6-v2     ChromaDB        "Explain recursion"
```

Day 2 gave us chunks. Day 3 embeds each chunk into a vector and stores it in a vector
database, then lets us search by **meaning** instead of keywords.

---

## Embeddings

Model: **`sentence-transformers/all-MiniLM-L6-v2`** — 384 dims, runs locally, fast.

- Embeddings are **L2-normalized** so cosine similarity behaves cleanly.
- The model loads once per process (lazy singleton) — first load downloads/caches the
  weights (~80 MB), after that it's instant.

`app/rag/embeddings.py`

```python
embedder = get_embedder()
vectors = embedder.embed(["chunk text", "another chunk"])  # -> list[list[float]]
```

---

## Vector database (ChromaDB)

`app/rag/vector_store.py` wraps a **persistent** ChromaDB collection:

- Persists to `backend/uploads/vectorstore/` (gitignored) so indexed docs survive restarts.
- Collection `documents`, configured with **cosine** distance (`hnsw:space: cosine`).
- Each chunk is stored with its embedding, text, and metadata
  (`document_id`, `filename`, `page`, `chunk_index`).

Cosine **distance** is converted to a **similarity** score in `[0, 1]`:
`similarity = max(0, 1 - distance)` (higher = more relevant).

> ChromaDB vs FAISS: ChromaDB ships with a built-in persistence layer and metadata
> filtering, which is exactly what we need here. FAISS is faster at massive scale but
> has no storage layer of its own.

---

## How it's wired in

Indexing now happens automatically inside the **upload** flow (Day 2 endpoint), so the
full `PDF → Chunks → Embeddings → Vector DB` pipeline runs on a single request:

- `DocumentService.save_and_process()` → after chunking, calls `VectorStore.add_chunks()`.
- The upload response now reports `indexed: true` and the `embedding_model` used.
- Indexing **degrades gracefully**: if embedding fails, the upload still succeeds with
  `indexed: false` (chunks are still saved).
- Deleting a document also removes its vectors from the store.

---

## Semantic Search API

| Method | Route | Description |
|--------|-------|-------------|
| `POST` | `/api/documents/search` | Body: `{ "query", "top_k", "document_id?" }` |
| `GET` | `/api/documents/search` | `?q=...&top_k=5&document_id=...` |

`document_id` is optional — omit it to search across all documents, or pass it to scope
the search to one document.

### Example

```bash
curl -X POST http://localhost:8000/api/documents/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Explain recursion", "top_k": 3}'
```

```json
{
  "query": "Explain recursion",
  "count": 3,
  "results": [
    {
      "chunk_id": "ab12cd34_0",
      "document_id": "ab12cd34",
      "filename": "lecture.pdf",
      "page": 1,
      "chunk_index": 0,
      "text": "Recursion is a programming technique where a function calls itself...",
      "similarity": 0.7667
    }
  ]
}
```

---

## Verified (smoke test)

Indexed a 4-topic lecture PDF (recursion, photosynthesis, water cycle, exam prep → 8
chunks) and confirmed meaning-based retrieval — queries match the right topic even with
**no shared keywords**:

| Query | Top match | Page | Similarity |
|-------|-----------|------|-----------|
| "Explain recursion" | Recursion | 1 | **0.77** |
| "How do plants make their food?" | Photosynthesis | 2 | **0.49** |
| "best way to revise before a test" | Exam preparation | 4 | **0.51** |

Document-scoped search and vector cleanup on delete also verified.

---

## Checklist

- [x] Generate embeddings (`all-MiniLM-L6-v2`)
- [x] Store in a vector DB (ChromaDB, persistent, cosine)
- [x] Pipeline `PDF → Chunks → Embeddings → Vector DB` (runs on upload)
- [x] Semantic Search endpoint (`/api/documents/search`)

---

## Next (Day 4)

LLM response generation — feed the retrieved chunks into an LLM to produce a grounded,
natural-language answer (`/rag/ask`), completing the full RAG loop.
