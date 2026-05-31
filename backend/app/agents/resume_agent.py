"""Resume Agent — CV tips and bullet rewrites (Week 6 · Day 1)."""

from __future__ import annotations

from app.rag.llm import call_llm, llm_enabled


async def run_resume_agent(message: str, resume_text: str | None = None) -> dict:
    text = (resume_text or message).strip()

    if llm_enabled():
        prompt = (
            "You are an expert resume coach for students and early-career engineers.\n"
            "Help improve resumes: strong action verbs, quantified impact, ATS keywords.\n"
            "If the user pasted resume content, give specific bullet rewrites.\n"
            "Otherwise answer their resume/CV question concisely.\n\n"
            f"USER INPUT:\n{text[:4000]}"
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
                "actions": [{"type": "tip", "topic": "resume"}],
            }

    return {
        "answer": (
            "**Resume tips**\n\n"
            "• Start bullets with strong verbs (Built, Led, Improved)\n"
            "• Quantify impact: users, %, time saved\n"
            "• Tailor keywords to the job description\n"
            "• Keep to 1 page for early career\n\n"
            "Paste a bullet or section and I'll rewrite it when the AI key is configured."
        ),
        "used_llm": False,
        "sub_intent": "tips",
        "actions": [],
    }
