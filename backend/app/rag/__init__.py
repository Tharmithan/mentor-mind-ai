"""Week 4 — RAG (Retrieval Augmented Generation) module.

Day 2: PDF processing — upload, extract text, chunk, persist.
"""

from app.rag.document_service import DocumentService
from app.rag.pdf_processor import PDFProcessor, ProcessedDocument, get_pdf_processor

__all__ = ["PDFProcessor", "ProcessedDocument", "get_pdf_processor", "DocumentService"]
