"""Agent router — classify intent and pick Study / Interview / Career / Resume (Week 6 · Day 1)."""

from __future__ import annotations

import re

from app.agents.types import AgentType, RouteDecision
from app.rag.llm import call_llm, llm_enabled, parse_json

_KEYWORDS: dict[AgentType, list[str]] = {
    AgentType.INTERVIEW: [
        "interview", "mock interview", "behavioral", "tell me about yourself",
        "star method", "hr question", "technical interview", "practice question",
        "interviewer", "salary negotiation",
    ],
    AgentType.STUDY: [
        "summarize", "summary", "quiz", "flashcard", "explain", "study",
        "revision", "notes", "learn", "chapter", "homework", "exam prep",
        "what is", "how does", "teach me", "exam in", "study plan", "days until",
        "weak subject", "learning goal", "track progress", "revision plan",
        "what should i study", "prepare for",
    ],
    AgentType.CAREER: [
        "career", "job", "internship", "roadmap", "skill gap", "performance",
        "grades", "improve", "focus", "recommend", "insight",
        "dashboard", "predict", "strong subject",
    ],
    AgentType.RESUME: [
        "resume", "cv", "curriculum vitae", "cover letter", "linkedin",
        "bullet point", "work experience", "projects section", "portfolio",
    ],
}


def _keyword_route(message: str, last_agent: str | None) -> RouteDecision:
    lower = message.lower()
    scores: dict[AgentType, float] = {a: 0.0 for a in AgentType}
    for agent, words in _KEYWORDS.items():
        for w in words:
            if w in lower:
                scores[agent] += 1.0 + len(w) * 0.01

    best = max(scores, key=scores.get)
    best_score = scores[best]
    if best_score == 0:
        # Default: continue last agent or career for open questions
        fallback = AgentType(last_agent) if last_agent in {a.value for a in AgentType} else AgentType.CAREER
        return RouteDecision(fallback, 0.45, "No strong keyword match — using context default")

    total = sum(scores.values()) or 1
    confidence = min(0.95, 0.5 + best_score / total * 0.45)
    return RouteDecision(best, round(confidence, 2), f"Keyword match for {best.value} agent")


async def _llm_route(message: str, history: list[dict], last_agent: str | None) -> RouteDecision | None:
    if not llm_enabled():
        return None
    hist = "\n".join(f"{m['role']}: {m['content'][:120]}" for m in history[-4:])
    prompt = (
        "Classify the user message into exactly one agent.\n"
        'Respond JSON: {"agent":"study|interview|career|resume","confidence":0.0-1.0,"reason":"..."}\n\n'
        f"Last agent: {last_agent or 'none'}\n"
        f"Recent:\n{hist}\n\n"
        f"User: {message}"
    )
    raw = await call_llm(
        [
            {"role": "system", "content": "Output valid JSON only."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=120,
        temperature=0.1,
        force_json=True,
    )
    data = parse_json(raw)
    if not data or data.get("agent") not in {a.value for a in AgentType}:
        return None
    return RouteDecision(
        AgentType(data["agent"]),
        float(data.get("confidence", 0.75)),
        str(data.get("reason", "LLM routing")),
    )


async def route_message(
    message: str,
    history: list[dict] | None = None,
    last_agent: str | None = None,
) -> RouteDecision:
    """Pick the best agent for a user message."""
    history = history or []
    text = message.strip()
    if not text:
        return RouteDecision(AgentType.CAREER, 0.5, "Empty message — default career agent")

    llm_decision = await _llm_route(text, history, last_agent)
    kw_decision = _keyword_route(text, last_agent)

    if llm_decision and llm_decision.confidence >= 0.65:
        return llm_decision
    if kw_decision.confidence >= 0.55:
        return kw_decision
    return llm_decision or kw_decision
