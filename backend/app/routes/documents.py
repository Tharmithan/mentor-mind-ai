"""Document/PDF processing routes (Week 4 · Day 2).

    POST   /api/documents/upload          upload + extract + chunk a PDF
    GET    /api/documents                 list processed documents
    GET    /api/documents/{id}/chunks     get all chunks for a document
    DELETE /api/documents/{id}            remove a document and its chunks
"""

from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from app.models.document import (
    ChatRequest,
    ChatResponse,
    ChunksResponse,
    DocumentListResponse,
    SearchRequest,
    SearchResponse,
    UploadResponse,
)
from app.rag.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])

MAX_UPLOAD_BYTES = 25 * 1024 * 1024  # 25 MB


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)) -> UploadResponse:
    """Upload a learning material (PDF/TXT/MD), extract text and split into chunks."""
    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File too large (max 25 MB).")
    try:
        return DocumentService.save_and_process(file.filename or "upload", content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - surfaces processing errors
        raise HTTPException(status_code=500, detail=f"Failed to process file: {exc}") from exc


@router.get("", response_model=DocumentListResponse)
async def list_documents() -> DocumentListResponse:
    """List all processed documents (most recent first)."""
    return DocumentService.list_documents()


@router.post("/search", response_model=SearchResponse)
async def search_documents(body: SearchRequest) -> SearchResponse:
    """Semantic search over indexed chunks (e.g. 'Explain recursion')."""
    try:
        return DocumentService.search(body.query, top_k=body.top_k, document_id=body.document_id)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Search failed: {exc}") from exc


@router.get("/search", response_model=SearchResponse)
async def search_documents_get(
    q: str = Query(..., min_length=1, description="Search query"),
    top_k: int = Query(5, ge=1, le=20),
    document_id: str | None = Query(None),
) -> SearchResponse:
    """Convenience GET for semantic search."""
    try:
        return DocumentService.search(q, top_k=top_k, document_id=document_id)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Search failed: {exc}") from exc


@router.post("/chat", response_model=ChatResponse)
async def chat_with_documents(body: ChatRequest) -> ChatResponse:
    """AI tutor chat — answers grounded in the student's uploaded notes (full RAG loop)."""
    try:
        return await DocumentService.chat(body)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Chat failed: {exc}") from exc


@router.get("/{document_id}/chunks", response_model=ChunksResponse)
async def get_document_chunks(document_id: str) -> ChunksResponse:
    """Return every stored chunk for a document."""
    result = DocumentService.get_chunks(document_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    return result


@router.delete("/{document_id}")
async def delete_document(document_id: str) -> dict:
    if not DocumentService.delete(document_id):
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"message": "Document deleted.", "document_id": document_id}
