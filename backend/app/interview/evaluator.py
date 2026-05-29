"""AI answer evaluation (Week 5 · Day 3).

Combines:
  - Heuristic metrics (length, grammar, structure, keyword match)
  - SentenceTransformer semantic similarity vs ideal answer
  - Optional LLM evaluation when OPENAI_API_KEY is set

Returns scores on a 0–100 scale plus ideal-answer comparison.
"""

from __future__ import annotations

import json
import os
import re

import httpx

from app.config import settings
from app.interview.analyzer import analyze_answer
from app.interview.question_bank import InterviewQuestion

# Per-question overrides live in questions.json; these are fallbacks.
_CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "introduction": ["background", "experience", "skills", "education", "passion"],
    "dsa": ["complexity", "algorithm", "data structure", "example", "time", "space"],
    "ai-ml": ["model", "training", "data", "overfitting", "accuracy", "feature"],
    "web-dev": ["api", "http", "rest", "client", "server", "database"],
    "teamwork": ["team", "collaborat", "communicat", "role", "project"],
    "leadership": ["led", "initiative", "decision", "team", "outcome"],
    "conflict": ["disagree", "resolved", "listen", "compromise", "outcome"],
    "growth": ["learned", "mistake", "improved", "feedback", "changed"],
}


def _keywords_for(q: InterviewQuestion) -> list[str]:
    if getattr(q, "expected_keywords", None):
        return list(q.expected_keywords)
    return _CATEGORY_KEYWORDS.get(q.category, [])


def _ideal_for(q: InterviewQuestion) -> str:
    ideal = getattr(q, "ideal_answer", None) or ""
    if ideal.strip():
        return ideal.strip()
    return (
        f"A strong answer to this {q.category} question should: {q.tips} "
        f"Address the question directly with a clear structure and a concrete example."
    )


def _grammar_score(text: str) -> float:
    """Simple grammar/clarity proxy (0–100)."""
    words = text.split()
    if len(words) < 5:
        return 35.0
    score = 50.0
    if re.search(r"[.!?]", text):
        score += 15
    if not re.search(r"\b(um|uh|like)\b", text, re.I):
        score += 10
    caps_ok = not re.search(r"[a-z][A-Z]", text)  # mid-word caps
    if caps_ok:
        score += 5
    avg_len = sum(len(w) for w in words) / len(words)
    if 3 < avg_len < 12:
        score += 10
    return min(100.0, score)


def _keyword_match_score(text: str, keywords: list[str]) -> tuple[float, list[str], list[str]]:
    lower = text.lower()
    matched = [k for k in keywords if k.lower() in lower]
    missing = [k for k in keywords if k.lower() not in lower]
    pct = (len(matched) / len(keywords) * 100) if keywords else 70.0
    return min(100.0, pct), matched, missing


def _semantic_similarity(answer: str, ideal: str) -> float:
    """Cosine similarity → 0–100 using the RAG embedder."""
    try:
        from app.rag.embeddings import get_embedder
        import numpy as np

        emb = get_embedder()
        a, b = emb.embed([answer, ideal])
        sim = float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
        return round(max(0.0, min(100.0, sim * 100)), 1)
    except Exception:
        return 55.0


async def _llm_evaluate(question: InterviewQuestion, answer: str, ideal: str) -> dict | None:
    api_key = os.getenv("OPENAI_API_KEY") or getattr(settings, "openai_api_key", None)
    if not api_key:
        return None
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    prompt = (
        "You are an expert interview coach. Score the candidate's answer.\n"
        "Respond in JSON only with keys:\n"
        '  "communication" (0-100), "technical_score" (0-100), "confidence" (0-100),\n'
        '  "relevance" (0-100), "grammar" (0-100), "clarity" (0-100),\n'
        '  "feedback_summary" (2 sentences), "strengths" (array of 2 strings),\n'
        '  "improvements" (array of 2 strings),\n'
        '  "expert_answer" (1 short paragraph — the ideal answer)\n\n'
        f"QUESTION: {question.text}\n"
        f"IDEAL OUTLINE: {ideal}\n"
        f"EXPECTED KEYWORDS: {', '.join(_keywords_for(question))}\n"
        f"CANDIDATE ANSWER: {answer}"
    )
    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(
                f"{base_url.rstrip('/')}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "Output valid JSON only."},
                        {"role": "user", "content": prompt},
                    ],
                    "max_tokens": 600,
                    "temperature": 0.3,
                    "response_format": {"type": "json_object"},
                },
            )
            resp.raise_for_status()
            raw = resp.json()["choices"][0]["message"]["content"]
            return json.loads(raw)
    except Exception:
        return None


def _to_pct(score_10: float) -> int:
    return int(round(min(10.0, max(0.0, score_10)) * 10))


async def evaluate_answer(question: InterviewQuestion, answer: str) -> dict:
    """Full evaluation payload for one interview turn."""
    text = answer.strip()
    base = analyze_answer(question, text)
    keywords = _keywords_for(question)
    ideal = _ideal_for(question)

    kw_score, matched_kw, missing_kw = _keyword_match_score(text, keywords)
    grammar = _grammar_score(text)
    clarity = _to_pct(base["communication_score"])
    relevance = _to_pct(base["technical_score"]) if question.interview_type == "technical" else _to_pct(
        min(10.0, base.get("overall_score", 5) + 1)
    )
    semantic_pct = _semantic_similarity(text, ideal)
    length_pct = min(100, int(len(text.split()) / 0.8))  # ~80 words → 100

    llm = await _llm_evaluate(question, text, ideal)
    if llm:
        communication = int(llm.get("communication", clarity))
        technical = int(llm.get("technical_score", relevance))
        confidence = int(llm.get("confidence", _to_pct(base["confidence_score"])))
        grammar = int(llm.get("grammar", grammar))
        clarity = int(llm.get("clarity", clarity))
        relevance = int(llm.get("relevance", relevance))
        expert = str(llm.get("expert_answer", ideal))
        summary = str(llm.get("feedback_summary", base["feedback_summary"]))
        strengths = list(llm.get("strengths", base["strengths"]))[:3]
        improvements = list(llm.get("improvements", base["improvements"]))[:3]
        used_llm = True
    else:
        communication = int((clarity + grammar) / 2)
        technical = int((relevance + kw_score + semantic_pct) / 3)
        confidence = _to_pct(base["confidence_score"])
        expert = ideal
        summary = base["feedback_summary"]
        strengths = base["strengths"]
        improvements = base["improvements"]
        used_llm = False

    overall_pct = int(
        (communication + technical + confidence + relevance + grammar) / 5
    )

    return {
        "overall_score": base["overall_score"],
        "communication_score": base["communication_score"],
        "technical_score": base["technical_score"],
        "confidence_score": base["confidence_score"],
        "feedback_summary": summary,
        "strengths": strengths,
        "improvements": improvements,
        "word_count": base["word_count"],
        "used_llm": used_llm,
        "scores": {
            "communication": communication,
            "technical_score": technical,
            "confidence": confidence,
            "relevance": relevance,
            "grammar": grammar,
            "clarity": clarity,
            "keyword_match": int(kw_score),
            "semantic_similarity": int(semantic_pct),
            "answer_length": length_pct,
            "overall": overall_pct,
        },
        "ideal_comparison": {
            "expert_answer": expert,
            "expected_keywords": keywords,
            "matched_keywords": matched_kw,
            "missing_keywords": missing_kw[:8],
            "similarity_pct": semantic_pct,
        },
    }
