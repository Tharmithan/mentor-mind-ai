"""Full resume analysis orchestration (Week 6 · Day 4)."""

from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.models.resume import (
    MissingSkill,
    ResumeAnalysisResponse,
    ResumeSection,
    WeakBullet,
)
from app.resume.ats_scorer import score_ats
from app.resume.feedback import generate_ai_feedback
from app.resume.parser import (
    RESUMES_DIR,
    WEAK_VERBS,
    extract_bullets,
    extract_text_from_file,
    parse_sections,
    save_upload,
)

# Skills recruiters expect by target role
ROLE_SKILLS: dict[str, list[tuple[str, str]]] = {
    "default": [
        ("Python", "high", "Add a project using Python (FastAPI, pandas, or ML)"),
        ("Git", "medium", "Mention version control in a project bullet"),
        ("SQL", "high", "Include database experience (PostgreSQL, SQLite)"),
        ("Machine Learning", "medium", "Highlight any ML coursework or Kaggle projects"),
        ("APIs", "medium", "Mention REST API or backend development"),
    ],
    "ai_engineer": [
        ("Python", "high", "Lead with Python + LLM/ML project bullets"),
        ("Machine Learning", "high", "Add model training or evaluation metrics"),
        ("LangChain / RAG", "medium", "Mention RAG, embeddings, or agent projects"),
        ("Docker", "medium", "Note containerized deployments"),
        ("PyTorch or TensorFlow", "medium", "Include deep learning framework experience"),
    ],
    "data_scientist": [
        ("Python", "high", "Show pandas, scikit-learn, or Jupyter projects"),
        ("Statistics", "high", "Reference statistical analysis or A/B testing"),
        ("SQL", "high", "Add data querying and pipeline examples"),
        ("Data Visualization", "medium", "Mention Matplotlib, Plotly, or dashboards"),
        ("Machine Learning", "high", "Quantify model performance (accuracy, F1, etc.)"),
    ],
    "software_engineer": [
        ("JavaScript or Python", "high", "Highlight primary language proficiency"),
        ("Data Structures & Algorithms", "high", "Reference LeetCode rank or DSA projects"),
        ("REST APIs", "high", "Describe API design and endpoints built"),
        ("Git", "medium", "Mention collaborative development workflow"),
        ("Testing", "medium", "Add unit/integration test experience"),
    ],
    "mlops": [
        ("Docker", "high", "Show containerized ML deployments"),
        ("CI/CD", "high", "Mention GitHub Actions or pipeline automation"),
        ("Python", "high", "Core language for ML pipelines"),
        ("Cloud (AWS/GCP)", "medium", "Add cloud deployment experience"),
        ("MLflow or Kubeflow", "medium", "Reference experiment tracking tools"),
    ],
}

TECH_KEYWORDS = re.compile(
    r"\b(python|java|javascript|typescript|react|node|sql|postgresql|mongodb|"
    r"docker|kubernetes|aws|gcp|azure|machine learning|deep learning|pytorch|"
    r"tensorflow|scikit|pandas|fastapi|flask|django|git|linux|api|rest|graphql|"
    r"langchain|rag|nlp|computer vision|opencv|mlops|ci/cd|github actions)\b",
    re.I,
)


class ResumeAnalyzer:
    @staticmethod
    async def analyze_text(
        text: str,
        filename: str | None = None,
        target_role: str | None = None,
        num_pages: int = 1,
    ) -> ResumeAnalysisResponse:
        text = text.strip()
        sections = parse_sections(text)
        ats_score, ats_grade, ats_checks = score_ats(text, sections)
        missing = ResumeAnalyzer._missing_skills(text, target_role)
        weak = ResumeAnalyzer._weak_bullets(text)
        formatting = ResumeAnalyzer._formatting_issues(text, sections, num_pages)

        headline, summary, feedback, used_llm = await generate_ai_feedback(
            text,
            ats_score,
            ats_checks,
            missing,
            weak,
            formatting,
            target_role,
        )

        analysis_id = uuid.uuid4().hex[:12]
        result = ResumeAnalysisResponse(
            analysis_id=analysis_id,
            filename=filename,
            word_count=len(text.split()),
            page_estimate=num_pages,
            sections=sections,
            ats_score=ats_score,
            ats_grade=ats_grade,
            ats_checks=ats_checks,
            missing_skills=missing,
            weak_bullets=weak,
            formatting_issues=formatting,
            feedback=feedback,
            summary=summary,
            headline=headline,
            used_llm=used_llm,
        )
        ResumeAnalyzer._persist(result, text)
        return result

    @staticmethod
    async def analyze_file(path: Path, target_role: str | None = None) -> ResumeAnalysisResponse:
        text, pages = extract_text_from_file(path)
        if len(text) < 50:
            raise ValueError("Could not extract enough text from the file. Try a text-based PDF.")
        return await ResumeAnalyzer.analyze_text(
            text, filename=path.name, target_role=target_role, num_pages=pages
        )

    @staticmethod
    async def analyze_upload(content: bytes, filename: str, target_role: str | None = None) -> ResumeAnalysisResponse:
        path = save_upload(filename, content)
        return await ResumeAnalyzer.analyze_file(path, target_role)

    @staticmethod
    def _missing_skills(text: str, target_role: str | None) -> list[MissingSkill]:
        lower = text.lower()
        role_key = (target_role or "default").lower().replace(" ", "_")
        for key in ROLE_SKILLS:
            if key in role_key or role_key in key:
                role_key = key
                break
        else:
            role_key = "default"

        missing: list[MissingSkill] = []
        for skill, importance, suggestion in ROLE_SKILLS.get(role_key, ROLE_SKILLS["default"]):
            if skill.lower() not in lower and not any(
                part in lower for part in skill.lower().split()
            ):
                missing.append(
                    MissingSkill(skill=skill, importance=importance, suggestion=suggestion)
                )
        return missing[:6]

    @staticmethod
    def _weak_bullets(text: str) -> list[WeakBullet]:
        weak: list[WeakBullet] = []
        from app.resume.ats_scorer import METRIC_RE

        for bullet in extract_bullets(text):
            bl = bullet.lower()
            if any(v in bl for v in WEAK_VERBS):
                weak.append(
                    WeakBullet(
                        text=bullet[:120],
                        issue="Passive or weak phrasing",
                        suggestion=f"Rewrite with a strong verb: 'Built', 'Led', 'Improved' — {bullet[:60]}…",
                    )
                )
            elif len(bullet) > 25 and not METRIC_RE.search(bullet):
                weak.append(
                    WeakBullet(
                        text=bullet[:120],
                        issue="Missing quantified impact",
                        suggestion="Add metrics: users served, % improvement, time saved, or scale.",
                    )
                )
            if len(weak) >= 5:
                break
        return weak

    @staticmethod
    def _formatting_issues(
        text: str, sections: list[ResumeSection], pages: int
    ) -> list[str]:
        issues: list[str] = []
        section_names = {s.name.lower() for s in sections}
        if not any("experience" in n or "work" in n for n in section_names):
            issues.append("Add a clearly labeled **Experience** section for ATS parsers.")
        if not any("skill" in n for n in section_names):
            issues.append("Add a **Skills** section with keywords matching your target role.")
        if pages > 2:
            issues.append("Resume appears long — aim for 1 page unless 5+ years experience.")
        if len(text.split()) < 150:
            issues.append("Resume is very short — expand project and experience descriptions.")
        caps_lines = sum(1 for line in text.splitlines() if line.isupper() and len(line) > 8)
        if caps_lines > 3:
            issues.append("Reduce ALL-CAPS headings — use Title Case for section headers.")
        if not TECH_KEYWORDS.search(text):
            issues.append("Add technical keywords (Python, SQL, ML, etc.) for ATS matching.")
        return issues[:5]

    @staticmethod
    def _persist(result: ResumeAnalysisResponse, raw_text: str) -> None:
        RESUMES_DIR.mkdir(parents=True, exist_ok=True)
        path = RESUMES_DIR / f"{result.analysis_id}.json"
        path.write_text(
            json.dumps(
                {
                    **result.model_dump(),
                    "raw_text_preview": raw_text[:500],
                    "saved_at": datetime.now(timezone.utc).isoformat(),
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    @staticmethod
    def get_analysis(analysis_id: str) -> ResumeAnalysisResponse | None:
        path = RESUMES_DIR / f"{analysis_id}.json"
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        data.pop("raw_text_preview", None)
        data.pop("saved_at", None)
        return ResumeAnalysisResponse(**data)

    @staticmethod
    def to_markdown(result: ResumeAnalysisResponse) -> str:
        lines = [
            f"## Resume Analysis — Grade **{result.ats_grade}** ({result.ats_score:.0f}/100 ATS)\n",
            f"_{result.headline}_\n",
            result.summary,
            "",
            "**Top recommendations**",
        ]
        for f in result.feedback[:5]:
            icon = "🔴" if f.priority == "high" else "🟡" if f.priority == "medium" else "🟢"
            lines.append(f"{icon} {f.message}")
        if result.missing_skills:
            lines.append("\n**Missing skills**")
            for m in result.missing_skills[:4]:
                lines.append(f"• **{m.skill}** ({m.importance}) — {m.suggestion}")
        if result.weak_bullets:
            lines.append("\n**Weak descriptions**")
            for w in result.weak_bullets[:3]:
                lines.append(f"• _{w.issue}_: {w.suggestion}")
        lines.append(f"\n_{result.word_count} words · ~{result.page_estimate} page(s)_")
        return "\n".join(lines)
