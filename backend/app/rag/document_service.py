"""Service layer for document upload + processing (Week 4 · Day 2).

Responsibilities:
  - save the uploaded file to ``backend/uploads/``
  - extract text and split it into chunks (PDFProcessor)
  - persist the processed chunks as JSON in ``backend/uploads/processed/``
  - list documents and fetch their chunks
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.models.document import (
    ChatRequest,
    ChatResponse,
    ChunksResponse,
    DocumentChunk,
    DocumentListResponse,
    DocumentMeta,
    SearchResponse,
    SearchResult,
    UploadResponse,
)
from app.rag.pdf_processor import get_pdf_processor

# backend/app/rag/document_service.py -> parents[2] == backend/
BACKEND_DIR = Path(__file__).resolve().parents[2]
UPLOADS_DIR = BACKEND_DIR / "uploads"
PROCESSED_DIR = UPLOADS_DIR / "processed"

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}
PREVIEW_CHUNKS = 3


class DocumentService:
    @staticmethod
    def _ensure_dirs() -> None:
        UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def save_and_process(filename: str, content: bytes) -> UploadResponse:
        DocumentService._ensure_dirs()

        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type '{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )
        if not content:
            raise ValueError("Uploaded file is empty.")

        document_id = uuid.uuid4().hex[:12]
        raw_path = UPLOADS_DIR / f"{document_id}{ext}"
        raw_path.write_bytes(content)

        try:
            processed = get_pdf_processor().process(raw_path)
        except Exception:
            # Don't leave an orphaned raw file if processing fails.
            raw_path.unlink(missing_ok=True)
            raise

        uploaded_at = datetime.now(timezone.utc).isoformat()
        chunks = [
            DocumentChunk(
                chunk_id=f"{document_id}_{c.chunk_index}",
                document_id=document_id,
                chunk_index=c.chunk_index,
                text=c.text,
                char_count=c.char_count,
                page=c.page,
            )
            for c in processed.chunks
        ]

        # PDF -> Chunks -> Embeddings -> Vector DB
        indexed, embedding_model = DocumentService._index(document_id, filename, chunks)

        meta = DocumentMeta(
            document_id=document_id,
            filename=filename,
            uploaded_at=uploaded_at,
            num_pages=processed.num_pages,
            num_chunks=processed.num_chunks,
            total_chars=processed.total_chars,
            chunk_size=processed.chunk_size,
            chunk_overlap=processed.chunk_overlap,
            indexed=indexed,
            embedding_model=embedding_model,
        )

        DocumentService._persist(meta, chunks, raw_filename=raw_path.name)

        note = " and indexed for semantic search" if indexed else ""
        return UploadResponse(
            message=f"Processed '{filename}' into {meta.num_chunks} chunks{note}.",
            document=meta,
            preview_chunks=chunks[:PREVIEW_CHUNKS],
        )

    @staticmethod
    def _index(document_id: str, filename: str, chunks: list[DocumentChunk]) -> tuple[bool, str | None]:
        """Embed + store chunks in the vector DB. Degrades gracefully on failure."""
        try:
            from app.rag.vector_store import get_vector_store

            store = get_vector_store()
            store.add_chunks(document_id, filename, chunks)
            return True, store.embedding_model
        except Exception as exc:  # pragma: no cover - keep upload working if indexing fails
            print(f"[rag] indexing failed for {document_id}: {exc}")
            return False, None

    @staticmethod
    def _persist(meta: DocumentMeta, chunks: list[DocumentChunk], raw_filename: str) -> None:
        payload = {
            "meta": meta.model_dump(),
            "raw_filename": raw_filename,
            "chunks": [c.model_dump() for c in chunks],
        }
        out_path = PROCESSED_DIR / f"{meta.document_id}.json"
        out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @staticmethod
    def _load(document_id: str) -> dict | None:
        path = PROCESSED_DIR / f"{document_id}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def list_documents() -> DocumentListResponse:
        DocumentService._ensure_dirs()
        docs: list[DocumentMeta] = []
        for path in PROCESSED_DIR.glob("*.json"):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                docs.append(DocumentMeta(**data["meta"]))
            except (json.JSONDecodeError, KeyError, TypeError):
                continue
        docs.sort(key=lambda d: d.uploaded_at, reverse=True)
        return DocumentListResponse(count=len(docs), documents=docs)

    @staticmethod
    def get_text(document_id: str, max_chars: int = 8000) -> tuple[str, str] | None:
        """Return (concatenated_text, filename) for a document, capped at max_chars."""
        data = DocumentService._load(document_id)
        if data is None:
            return None
        parts: list[str] = []
        total = 0
        for c in data["chunks"]:
            t = c["text"].strip()
            if total + len(t) > max_chars:
                parts.append(t[: max(0, max_chars - total)])
                break
            parts.append(t)
            total += len(t)
        return "\n\n".join(parts), data["meta"]["filename"]

    @staticmethod
    def get_chunks(document_id: str) -> ChunksResponse | None:
        data = DocumentService._load(document_id)
        if data is None:
            return None
        chunks = [DocumentChunk(**c) for c in data["chunks"]]
        return ChunksResponse(
            document_id=document_id,
            filename=data["meta"]["filename"],
            num_chunks=len(chunks),
            chunks=chunks,
        )

    @staticmethod
    def search(query: str, top_k: int = 5, document_id: str | None = None) -> SearchResponse:
        """Semantic search across indexed document chunks."""
        from app.rag.vector_store import get_vector_store

        hits = get_vector_store().search(query, top_k=top_k, document_id=document_id)
        results = [SearchResult(**h) for h in hits]
        return SearchResponse(query=query, count=len(results), results=results)

    # Short follow-ups that rely on the previous turn's topic.
    _FOLLOWUP_HINTS = (
        "example", "more", "explain", "why", "how", "what about", "that", "it",
        "elaborate", "continue", "simpler", "again", "summarize",
    )

    @staticmethod
    def _retrieval_query(question: str, recent_topic: str | None) -> str:
        """Resolve follow-ups (e.g. 'give an example') by folding in the prior topic."""
        if not recent_topic:
            return question
        q = question.lower().strip()
        is_followup = len(q.split()) <= 5 or any(h in q for h in DocumentService._FOLLOWUP_HINTS)
        return f"{recent_topic} {question}" if is_followup else question

    @staticmethod
    async def chat(req: ChatRequest) -> ChatResponse:
        """Full RAG loop with conversation memory:
        recall session -> context-aware search -> LLM (with history) -> store turn.
        """
        from app.rag.llm import generate_answer
        from app.rag.memory import get_memory
        from app.rag.vector_store import get_vector_store

        memory = get_memory()
        session = memory.get_or_create(req.session_id)

        # Use prior history from memory; fall back to the request's history if sessionless.
        history = session.buffer(limit=12)
        if not history and req.history:
            history = [m.model_dump() for m in req.history]

        # Context-aware retrieval so "give an example" still finds the prior topic.
        search_query = DocumentService._retrieval_query(req.question, session.recent_topic())
        doc_id = req.document_id or session.last_document_id
        hits = get_vector_store().search(search_query, top_k=req.top_k, document_id=doc_id)

        session.add_user(req.question, document_id=req.document_id)
        result = await generate_answer(req.question, hits, history=history, mode=req.mode)
        session.add_ai(result["answer"])
        memory.save(session)

        return ChatResponse(
            answer=result["answer"],
            used_llm=result["used_llm"],
            model=result.get("model"),
            sources=[SearchResult(**h) for h in hits],
            session_id=session.session_id,
        )

    @staticmethod
    def delete(document_id: str) -> bool:
        data = DocumentService._load(document_id)
        if data is None:
            return False
        raw = UPLOADS_DIR / data.get("raw_filename", "")
        if raw.name:
            raw.unlink(missing_ok=True)
        (PROCESSED_DIR / f"{document_id}.json").unlink(missing_ok=True)
        try:
            from app.rag.vector_store import get_vector_store

            get_vector_store().delete_document(document_id)
        except Exception as exc:  # pragma: no cover
            print(f"[rag] vector delete failed for {document_id}: {exc}")
        return True
