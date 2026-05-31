"""Resume text extraction and section parsing (Week 6 · Day 4)."""

from __future__ import annotations

import re
import uuid
from pathlib import Path

from app.models.resume import ResumeSection
from app.rag.pdf_processor import get_pdf_processor

RESUMES_DIR = Path(__file__).resolve().parents[2] / "uploads" / "resumes"

SECTION_HEADERS = re.compile(
    r"(?im)^\s*(experience|work experience|employment|education|skills|"
    r"technical skills|projects|certifications|summary|profile|objective|"
    r"achievements|volunteer|interests|languages)\s*[:\-]?\s*$"
)

WEAK_VERBS = {
    "helped", "worked on", "responsible for", "assisted", "participated",
    "was involved", "handled", "did", "made", "used",
}

STRONG_VERBS = {
    "built", "developed", "designed", "implemented", "led", "improved",
    "optimized", "deployed", "created", "automated", "achieved", "reduced",
    "increased", "engineered", "architected", "launched", "scaled",
}


def extract_text_from_file(path: Path) -> tuple[str, int]:
    """Return (full_text, num_pages)."""
    processor = get_pdf_processor()
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        pages = processor._load_pdf(path)
        text = "\n\n".join(t for _, t in pages if t.strip())
        return text.strip(), len(pages)
    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="ignore").strip(), 1
    raise ValueError("Unsupported file type. Upload PDF, TXT, or MD.")


def parse_sections(text: str) -> list[ResumeSection]:
    lines = text.splitlines()
    sections: list[ResumeSection] = []
    current_name = "Header"
    current_lines: list[str] = []

    for line in lines:
        if SECTION_HEADERS.match(line.strip()):
            if current_lines:
                content = "\n".join(current_lines).strip()
                sections.append(
                    ResumeSection(
                        name=current_name,
                        content=content,
                        line_count=len([l for l in current_lines if l.strip()]),
                    )
                )
            current_name = line.strip().rstrip(":").title()
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines:
        content = "\n".join(current_lines).strip()
        sections.append(
            ResumeSection(
                name=current_name,
                content=content,
                line_count=len([l for l in current_lines if l.strip()]),
            )
        )

    if len(sections) <= 1 and not SECTION_HEADERS.search(text):
        return [ResumeSection(name="Full Resume", content=text, line_count=len(lines))]
    return sections


def extract_bullets(text: str) -> list[str]:
    bullets: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if re.match(r"^[\-\•\*●◦]\s+", stripped) or re.match(r"^\d+[\.\)]\s+", stripped):
            bullets.append(re.sub(r"^[\-\•\*●◦]\s+|^\d+[\.\)]\s+", "", stripped))
        elif len(stripped) > 40 and stripped[0].isupper() and "." in stripped:
            bullets.append(stripped)
    return bullets[:30]


def save_upload(filename: str, content: bytes) -> Path:
    RESUMES_DIR.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^\w.\-]", "_", filename)[:80]
    path = RESUMES_DIR / f"{uuid.uuid4().hex[:10]}_{safe}"
    path.write_bytes(content)
    return path
