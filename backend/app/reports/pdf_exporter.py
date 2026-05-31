"""PDF export for reports (Week 7 · Day 4)."""

from __future__ import annotations

from pathlib import Path


def _ascii_safe(text: str) -> str:
    replacements = {
        "\u2014": "-",
        "\u2013": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2026": "...",
        "**": "",
        "*": "",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return text.encode("ascii", errors="replace").decode("ascii").strip()


def markdown_to_pdf(markdown: str, output_path: Path, title: str = "MentorMind AI Report") -> bool:
    """Convert markdown-ish text to PDF using fpdf2. Returns False if fpdf2 unavailable."""
    try:
        from fpdf import FPDF
    except ImportError:
        return False

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_margins(20, 20, 20)
    pdf.add_page()
    width = pdf.w - pdf.l_margin - pdf.r_margin

    pdf.set_font("Helvetica", "B", 16)
    pdf.multi_cell(width, 10, _ascii_safe(title))
    pdf.ln(6)
    pdf.set_font("Helvetica", size=10)

    for raw in markdown.splitlines():
        line = _ascii_safe(raw)
        if not line or line == "---":
            pdf.ln(3)
            continue
        if line.startswith("# "):
            pdf.set_font("Helvetica", "B", 14)
            pdf.multi_cell(width, 8, line[2:])
            pdf.set_font("Helvetica", size=10)
        elif line.startswith("## "):
            pdf.set_font("Helvetica", "B", 12)
            pdf.multi_cell(width, 7, line[3:])
            pdf.set_font("Helvetica", size=10)
        elif line.startswith("- "):
            pdf.multi_cell(width, 6, f"  - {line[2:]}")
        else:
            pdf.multi_cell(width, 6, line)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(output_path))
    return True
