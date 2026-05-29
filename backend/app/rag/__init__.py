"""Week 4 — RAG (Retrieval Augmented Generation) module.

Day 2: PDF processing — upload, extract text, chunk, persist.
"""

from app.rag.document_service import DocumentService
from app.rag.embeddings import Embedder, get_embedder
from app.rag.pdf_processor import PDFProcessor, ProcessedDocument, get_pdf_processor
from app.rag.vector_store import VectorStore, get_vector_store

__all__ = [
    "PDFProcessor",
    "ProcessedDocument",
    "get_pdf_processor",
    "DocumentService",
    "Embedder",
    "get_embedder",
    "VectorStore",
    "get_vector_store",
]
