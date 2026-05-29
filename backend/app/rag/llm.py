"""LLM answer generation for the RAG chat assistant (Week 4 · Day 4).

Flow:  question + retrieved chunks  ->  prompt  ->  LLM  ->  grounded answer.

Uses an OpenAI-compatible API when ``OPENAI_API_KEY`` is set. Without a key it
falls back to an extractive answer built from the retrieved chunks, so the
assistant still works offline (just less conversational).
"""

from __future__ import annotations

import json
import os

import httpx

from app.config import settings


def llm_enabled() -> bool:
    return bool(os.getenv("OPENAI_API_KEY") or getattr(settings, "openai_api_key", None))


async def call_llm(
    messages: list[dict],
    max_tokens: int = 700,
    temperature: float = 0.4,
    force_json: bool = False,
) -> str | None:
    """Low-level OpenAI-compatible chat call. Returns content, or None if unavailable."""
    api_key = os.getenv("OPENAI_API_KEY") or getattr(settings, "openai_api_key", None)
    if not api_key:
        return None

    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    payload: dict = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    if force_json:
        payload["response_format"] = {"type": "json_object"}

    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(
                f"{base_url.rstrip('/')}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
    except Exception:  # pragma: no cover - network/LLM failures
        return None


def parse_json(text: str | None) -> dict | None:
    """Parse JSON from an LLM response, tolerating markdown code fences."""
    if not text:
        return None
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```", 2)[1] if "```" in cleaned else cleaned
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip("`").strip()
    try:
        return json.loads(cleaned)
    except (json.JSONDecodeError, TypeError):
        # last resort: grab the outermost {...}
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start != -1 and end > start:
            try:
                return json.loads(cleaned[start : end + 1])
            except json.JSONDecodeError:
                return None
        return None

MODE_INSTRUCTIONS = {
    "explain": "Explain the concept clearly and simply, as a tutor would to a student.",
    "summarize": "Summarize the key points concisely using short bullet points.",
    "example": "Give one or two concrete, easy-to-follow examples.",
}

SYSTEM_PROMPT = (
    "You are MentorMind AI, a friendly and encouraging study tutor. "
    "Answer the student's question using the CONTEXT from their uploaded notes below. "
    "Prefer the context; if it doesn't fully cover the question, you may add a brief "
    "general explanation but clearly say it's beyond their notes. "
    "Be clear and concise, and use examples when helpful."
)


def _build_context(chunks: list[dict]) -> str:
    if not chunks:
        return "(no relevant notes found)"
    lines = []
    for i, c in enumerate(chunks, 1):
        page = c.get("page")
        loc = f" (p.{page})" if page else ""
        lines.append(f"[{i}]{loc} {c['text'].strip()}")
    return "\n\n".join(lines)


def _fallback_answer(question: str, chunks: list[dict]) -> str:
    """Extractive answer when no LLM is configured."""
    if not chunks:
        return (
            "I couldn't find anything about that in your uploaded notes. "
            "Try uploading the relevant material, or rephrase your question."
        )
    top = chunks[0]["text"].strip()
    extra = ""
    if len(chunks) > 1:
        extra = "\n\nRelated note:\n" + chunks[1]["text"].strip()[:300]
    return (
        f"Here's the most relevant passage from your notes for \u201c{question}\u201d:\n\n"
        f"{top[:600]}{extra}\n\n"
        "(Tip: set an OPENAI_API_KEY to get fully conversational, summarized answers.)"
    )


async def generate_answer(
    question: str,
    chunks: list[dict],
    history: list[dict] | None = None,
    mode: str | None = None,
) -> dict:
    """Return {answer, used_llm, model}."""
    api_key = os.getenv("OPENAI_API_KEY") or getattr(settings, "openai_api_key", None)
    if not api_key:
        return {"answer": _fallback_answer(question, chunks), "used_llm": False, "model": None}

    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    context = _build_context(chunks)
    system = SYSTEM_PROMPT
    if mode in MODE_INSTRUCTIONS:
        system = f"{system}\n\nTask: {MODE_INSTRUCTIONS[mode]}"

    messages = [{"role": "system", "content": system}]
    for turn in (history or [])[-6:]:
        role = turn.get("role")
        content = turn.get("content")
        if role in {"user", "assistant"} and content:
            messages.append({"role": role, "content": content})
    messages.append(
        {
            "role": "user",
            "content": f"CONTEXT FROM MY NOTES:\n{context}\n\nQUESTION: {question}",
        }
    )

    try:
        async with httpx.AsyncClient(timeout=40.0) as client:
            resp = await client.post(
                f"{base_url.rstrip('/')}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": model,
                    "messages": messages,
                    "max_tokens": 600,
                    "temperature": 0.4,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            answer = data["choices"][0]["message"]["content"].strip()
            return {"answer": answer, "used_llm": True, "model": model}
    except Exception as exc:  # pragma: no cover - network/LLM failures
        fallback = _fallback_answer(question, chunks)
        return {
            "answer": f"{fallback}\n\n(LLM request failed: {exc})",
            "used_llm": False,
            "model": None,
        }
