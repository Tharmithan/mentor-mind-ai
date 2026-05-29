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
    indexed: bool = False
    embedding_model: str | None = None


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


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    document_id: str | None = None


class SearchResult(BaseModel):
    chunk_id: str
    document_id: str
    filename: str
    page: int | None = None
    chunk_index: int
    text: str
    similarity: float


class SearchResponse(BaseModel):
    query: str
    count: int
    results: list[SearchResult]


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int = Field(default=4, ge=1, le=10)
    document_id: str | None = None
    mode: str | None = None  # "explain" | "summarize" | "example"
    history: list[ChatMessage] | None = None


class ChatResponse(BaseModel):
    answer: str
    used_llm: bool
    model: str | None = None
    sources: list[SearchResult] = Field(default_factory=list)
