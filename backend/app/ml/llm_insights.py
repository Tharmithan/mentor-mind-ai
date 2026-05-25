"""Optional LLM layer — convert analytics JSON into natural language reports."""

from __future__ import annotations

import json
import os

import httpx

from app.config import settings


async def generate_llm_report(analytics_payload: dict) -> str | None:
    """
    Call OpenAI-compatible API when OPENAI_API_KEY is set.
    Returns None if unavailable — caller uses template report.
    """
    api_key = os.getenv("OPENAI_API_KEY") or getattr(settings, "openai_api_key", None)
    if not api_key:
        return None

    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    summary = analytics_payload.get("performance_summary", {})
    insights = analytics_payload.get("insights", [])[:6]
    prompt = (
        "You are MentorMind AI, a learning coach. Write a concise, encouraging "
        "performance report (3 short paragraphs + 3 bullet insights) based on this JSON. "
        "Use second person ('you'). Be specific with numbers.\n\n"
        f"Summary: {json.dumps(summary)}\n"
        f"Insights: {json.dumps([i.get('message') for i in insights])}\n"
        f"Cohort: {json.dumps(analytics_payload.get('cohort_stats', {}))}"
    )

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{base_url.rstrip('/')}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "Write clear, human SaaS-style analytics copy."},
                        {"role": "user", "content": prompt},
                    ],
                    "max_tokens": 500,
                    "temperature": 0.6,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return None
