"""PDF processing core for the RAG pipeline (Week 4 · Day 2).

Pipeline:  load PDF  ->  extract text per page  ->  split into chunks  ->  return chunks.

Chunking strategy matters. Defaults follow the recommended config:
    chunk_size = 500
    chunk_overlap = 50
The overlap keeps context from being cut mid-idea between adjacent chunks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

# LangChain moved these across versions; import defensively.
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:  # pragma: no cover - older langchain
    from langchain.text_splitter import RecursiveCharacterTextSplitter

DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 50


@dataclass
class Chunk:
    chunk_index: int
    text: str
    page: int | None = None

    @property
    def char_count(self) -> int:
        return len(self.text)


@dataclass
class ProcessedDocument:
    filename: str
    num_pages: int
    chunks: list[Chunk] = field(default_factory=list)
    chunk_size: int = DEFAULT_CHUNK_SIZE
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP

    @property
    def num_chunks(self) -> int:
        return len(self.chunks)

    @property
    def total_chars(self) -> int:
        return sum(c.char_count for c in self.chunks)


class PDFProcessor:
    """Extracts text from PDFs (or .txt) and splits it into overlapping chunks."""

    def __init__(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    ) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            # Split on natural boundaries first, fall back to characters.
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def process(self, file_path: str | Path) -> ProcessedDocument:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        suffix = path.suffix.lower()
        if suffix == ".pdf":
            pages = self._load_pdf(path)
        elif suffix in {".txt", ".md"}:
            pages = self._load_text(path)
        else:
            raise ValueError(f"Unsupported file type '{suffix}'. Use .pdf, .txt or .md.")

        chunks = self._split(pages)
        return ProcessedDocument(
            filename=path.name,
            num_pages=len(pages),
            chunks=chunks,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )

    @staticmethod
    def _load_pdf(path: Path) -> list[tuple[int, str]]:
        """Return [(page_number, page_text), ...] using LangChain's PyPDFLoader."""
        from langchain_community.document_loaders import PyPDFLoader

        loader = PyPDFLoader(str(path))
        docs = loader.load()  # one Document per page
        pages: list[tuple[int, str]] = []
        for i, doc in enumerate(docs):
            page_no = doc.metadata.get("page", i)
            # pypdf pages are 0-indexed; present them 1-indexed to users.
            pages.append((int(page_no) + 1, doc.page_content or ""))
        return pages

    @staticmethod
    def _load_text(path: Path) -> list[tuple[int, str]]:
        return [(1, path.read_text(encoding="utf-8", errors="ignore"))]

    def _split(self, pages: list[tuple[int, str]]) -> list[Chunk]:
        chunks: list[Chunk] = []
        index = 0
        for page_no, text in pages:
            if not text or not text.strip():
                continue
            for piece in self.splitter.split_text(text):
                piece = piece.strip()
                if not piece:
                    continue
                chunks.append(Chunk(chunk_index=index, text=piece, page=page_no))
                index += 1
        return chunks


_processor: PDFProcessor | None = None


def get_pdf_processor() -> PDFProcessor:
    """Singleton processor with the recommended 500/50 chunk config."""
    global _processor
    if _processor is None:
        _processor = PDFProcessor()
    return _processor
