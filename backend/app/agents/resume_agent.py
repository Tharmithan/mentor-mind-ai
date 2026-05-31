"""Resume Agent — upload analysis, ATS scoring, AI feedback (Week 6 · Day 4)."""

from __future__ import annotations

import re

from app.rag.llm import call_llm, llm_enabled
from app.resume.analyzer import ResumeAnalyzer


async def run_resume_agent(message: str, resume_text: str | None = None) -> dict:
    lower = message.lower()

    # Full analysis when resume text is provided (from upload or paste)
    text = (resume_text or "").strip()
    if len(text) >= 50 or re.search(r"\b(analyze|review|ats|score|check)\b.*\b(resume|cv)\b", lower):
        analyze_text = text if len(text) >= 50 else message
        if len(analyze_text) >= 50:
            target = _parse_target_role(message)
            result = await ResumeAnalyzer.analyze_text(analyze_text, target_role=target)
            return {
                "answer": ResumeAnalyzer.to_markdown(result),
                "used_llm": result.used_llm,
                "sub_intent": "resume_analysis",
                "data": {"analysis_id": result.analysis_id, "ats_score": result.ats_score},
                "actions": [
                    {"type": "navigate", "path": "/resume"},
                    {"type": "analysis", "session_id": result.analysis_id},
                ],
            }

    if re.search(r"\b(upload|pdf|resume analyzer|analyze my resume)\b", lower):
        return {
            "answer": (
                "**Resume Analyzer** — upload your PDF for instant feedback.\n\n"
                "I'll check:\n"
                "• Missing skills for your target role\n"
                "• ATS compatibility score\n"
                "• Formatting issues\n"
                "• Weak bullet descriptions\n\n"
                "Open [/resume](/resume) to upload, or paste your resume text here."
            ),
            "used_llm": False,
            "sub_intent": "upload_prompt",
            "actions": [{"type": "navigate", "path": "/resume"}],
        }

    if llm_enabled():
        prompt = (
            "You are an expert resume coach for students and early-career engineers.\n"
            "Help improve resumes: strong action verbs, quantified impact, ATS keywords.\n"
            "If the user pasted resume content, give specific bullet rewrites.\n"
            "Otherwise answer their resume/CV question concisely.\n\n"
            f"USER INPUT:\n{(text or message)[:4000]}"
        )
        raw = await call_llm(
            [
                {"role": "system", "content": "Be specific and encouraging."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=600,
        )
        if raw:
            return {
                "answer": raw,
                "used_llm": True,
                "sub_intent": "resume_review",
                "actions": [{"type": "navigate", "path": "/resume"}],
            }

    return {
        "answer": (
            "**Resume Analyzer**\n\n"
            "• Upload a PDF at [/resume](/resume) for ATS score + AI feedback\n"
            "• Start bullets with strong verbs (Built, Led, Improved)\n"
            "• Quantify impact: users, %, time saved\n"
            "• Tailor keywords to the job description\n\n"
            "Try: _\"Analyze my resume\"_ after uploading, or paste a bullet for rewriting."
        ),
        "used_llm": False,
        "sub_intent": "tips",
        "actions": [{"type": "navigate", "path": "/resume"}],
    }


def _parse_target_role(message: str) -> str | None:
    lower = message.lower()
    for role in ("ai engineer", "data scientist", "mlops", "software engineer"):
        if role in lower:
            return role
    return None
