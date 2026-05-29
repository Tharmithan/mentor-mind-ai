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
    ChunksResponse,
    DocumentChunk,
    DocumentListResponse,
    DocumentMeta,
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

        meta = DocumentMeta(
            document_id=document_id,
            filename=filename,
            uploaded_at=uploaded_at,
            num_pages=processed.num_pages,
            num_chunks=processed.num_chunks,
            total_chars=processed.total_chars,
            chunk_size=processed.chunk_size,
            chunk_overlap=processed.chunk_overlap,
        )

        DocumentService._persist(meta, chunks, raw_filename=raw_path.name)

        return UploadResponse(
            message=f"Processed '{filename}' into {meta.num_chunks} chunks.",
            document=meta,
            preview_chunks=chunks[:PREVIEW_CHUNKS],
        )

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
    def delete(document_id: str) -> bool:
        data = DocumentService._load(document_id)
        if data is None:
            return False
        raw = UPLOADS_DIR / data.get("raw_filename", "")
        if raw.name:
            raw.unlink(missing_ok=True)
        (PROCESSED_DIR / f"{document_id}.json").unlink(missing_ok=True)
        return True
