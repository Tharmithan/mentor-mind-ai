"""Pydantic models for the document/PDF processing API (Week 4 · Day 2)."""

from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    chunk_id: str
    document_id: str
    chunk_index: int
    text: str
    char_count: int
    page: int | None = None


class DocumentMeta(BaseModel):
    document_id: str
    filename: str
    uploaded_at: str
    num_pages: int
    num_chunks: int
    total_chars: int
    chunk_size: int
    chunk_overlap: int


class UploadResponse(BaseModel):
    message: str
    document: DocumentMeta
    preview_chunks: list[DocumentChunk] = Field(default_factory=list)


class DocumentListResponse(BaseModel):
    count: int
    documents: list[DocumentMeta]


class ChunksResponse(BaseModel):
    document_id: str
    filename: str
    num_chunks: int
    chunks: list[DocumentChunk]
