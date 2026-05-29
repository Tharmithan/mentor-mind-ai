"""Smart Learning Features generators (Week 4 · Day 5).

Each tool gathers content (a whole document and/or semantically-retrieved chunks),
asks the LLM for a structured result, and falls back to a sensible extractive
heuristic when no LLM key is configured — so every feature works offline too.
"""

from __future__ import annotations

import re

from app.models.study_tools import (
    ExplainSimpleResponse,
    Flashcard,
    FlashcardResponse,
    QuizQuestion,
    QuizResponse,
    RevisionResponse,
    StudyToolRequest,
    SummaryResponse,
)
from app.rag.llm import call_llm, parse_json

_SENT_RE = re.compile(r"(?<=[.!?])\s+")
_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "of", "to", "in", "on", "for", "is", "are",
    "was", "were", "it", "its", "as", "that", "this", "with", "by", "from", "into",
    "than", "then", "them", "they", "you", "your", "can", "will", "be", "has", "have",
}


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENT_RE.split(text) if len(s.strip()) > 25]


def _content_for(req: StudyToolRequest, default_chars: int = 8000) -> tuple[str, str | None]:
    """Return (content_text, source_label) from a document and/or a topic query."""
    from app.rag.document_service import DocumentService

    text_parts: list[str] = []
    source: str | None = None

    if req.document_id:
        got = DocumentService.get_text(req.document_id, max_chars=default_chars)
        if got:
            text_parts.append(got[0])
            source = got[1]

    if req.topic:
        from app.rag.vector_store import get_vector_store

        hits = get_vector_store().search(req.topic, top_k=5, document_id=req.document_id)
        if hits:
            text_parts.append("\n\n".join(h["text"] for h in hits))
            source = source or (hits[0].get("filename"))

    return ("\n\n".join(p for p in text_parts if p).strip(), source)


# --------------------------------------------------------------------------- #
# 1. AI Summarizer
# --------------------------------------------------------------------------- #
async def summarize(req: StudyToolRequest) -> SummaryResponse:
    content, source = _content_for(req)
    title = source or req.topic or "Summary"

    prompt = (
        "Summarize the following study material for a student. Respond in JSON with keys: "
        '"summary" (2-4 sentence paragraph) and "key_points" (array of 4-7 short bullet strings).\n\n'
        f"MATERIAL:\n{content[:7000]}"
    )
    raw = await call_llm(
        [
            {"role": "system", "content": "You are a concise study assistant. Output valid JSON only."},
            {"role": "user", "content": prompt},
        ],
        force_json=True,
    )
    data = parse_json(raw)
    if data and "summary" in data:
        return SummaryResponse(
            title=title,
            summary=str(data.get("summary", "")).strip(),
            key_points=[str(k).strip() for k in data.get("key_points", [])][:7],
            used_llm=True,
            source=source,
        )

    # Fallback: extractive
    sents = _sentences(content)
    summary = " ".join(sents[:3]) if sents else "No content available to summarize."
    key_points = [s[:140] for s in sents[:6]]
    return SummaryResponse(
        title=title, summary=summary, key_points=key_points, used_llm=False, source=source
    )


# --------------------------------------------------------------------------- #
# 2. Quiz Generator (MCQs)
# --------------------------------------------------------------------------- #
async def generate_quiz(req: StudyToolRequest) -> QuizResponse:
    content, source = _content_for(req)
    n = req.count

    prompt = (
        f"Create {n} multiple-choice quiz questions from the study material below. "
        "Respond in JSON with key \"questions\": an array of objects with keys "
        '"question" (string), "options" (array of exactly 4 strings), '
        '"answer_index" (0-3 integer of the correct option), and "explanation" (short string).\n\n'
        f"MATERIAL:\n{content[:7000]}"
    )
    raw = await call_llm(
        [
            {"role": "system", "content": "You are a quiz generator. Output valid JSON only."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1200,
        temperature=0.5,
        force_json=True,
    )
    data = parse_json(raw)
    if data and isinstance(data.get("questions"), list):
        questions = []
        for q in data["questions"][:n]:
            opts = [str(o) for o in q.get("options", [])][:4]
            if len(opts) < 2:
                continue
            ai = int(q.get("answer_index", 0))
            ai = ai if 0 <= ai < len(opts) else 0
            questions.append(
                QuizQuestion(
                    question=str(q.get("question", "")).strip(),
                    options=opts,
                    answer_index=ai,
                    explanation=(str(q["explanation"]).strip() if q.get("explanation") else None),
                )
            )
        if questions:
            return QuizResponse(questions=questions, used_llm=True, source=source)

    # Fallback: fill-in-the-keyword MCQs from sentences
    return QuizResponse(
        questions=_fallback_quiz(content, n), used_llm=False, source=source
    )


def _fallback_quiz(content: str, n: int) -> list[QuizQuestion]:
    sents = _sentences(content)
    questions: list[QuizQuestion] = []
    used_keywords: list[str] = []
    for s in sents:
        if len(questions) >= n:
            break
        words = [w for w in re.findall(r"[A-Za-z]{5,}", s) if w.lower() not in _STOPWORDS]
        if not words:
            continue
        answer = max(words, key=len)
        if answer in used_keywords:
            continue
        used_keywords.append(answer)
        blanked = re.sub(re.escape(answer), "______", s, count=1)
        distractors = [w for w in used_keywords if w != answer][:3]
        while len(distractors) < 3:
            distractors.append(f"option{len(distractors) + 1}")
        options = [answer, *distractors[:3]]
        questions.append(
            QuizQuestion(
                question=f"Fill in the blank: {blanked}",
                options=options,
                answer_index=0,
                explanation="Recall from the source material.",
            )
        )
    return questions


# --------------------------------------------------------------------------- #
# 3. Flashcard Generator
# --------------------------------------------------------------------------- #
async def generate_flashcards(req: StudyToolRequest) -> FlashcardResponse:
    content, source = _content_for(req)
    n = req.count

    prompt = (
        f"Create {n} revision flashcards from the study material below. "
        'Respond in JSON with key "flashcards": an array of objects with keys '
        '"front" (a question or term) and "back" (the concise answer/definition).\n\n'
        f"MATERIAL:\n{content[:7000]}"
    )
    raw = await call_llm(
        [
            {"role": "system", "content": "You create study flashcards. Output valid JSON only."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1000,
        force_json=True,
    )
    data = parse_json(raw)
    if data and isinstance(data.get("flashcards"), list):
        cards = [
            Flashcard(front=str(c.get("front", "")).strip(), back=str(c.get("back", "")).strip())
            for c in data["flashcards"][:n]
            if c.get("front") and c.get("back")
        ]
        if cards:
            return FlashcardResponse(flashcards=cards, used_llm=True, source=source)

    # Fallback: "X is Y" -> front/back, else sentence Q/A
    cards: list[Flashcard] = []
    for s in _sentences(content):
        if len(cards) >= n:
            break
        m = re.match(r"(.{3,60}?)\s+(?:is|are|means|refers to)\s+(.+)", s, re.IGNORECASE)
        if m:
            cards.append(Flashcard(front=f"What is {m.group(1).strip()}?", back=s))
        else:
            front = " ".join(s.split(" ")[:6]) + "…"
            cards.append(Flashcard(front=front, back=s))
    return FlashcardResponse(flashcards=cards, used_llm=False, source=source)


# --------------------------------------------------------------------------- #
# 4. Explain Like a Beginner
# --------------------------------------------------------------------------- #
async def explain_simple(concept: str, document_id: str | None = None) -> ExplainSimpleResponse:
    context, _ = _content_for(StudyToolRequest(document_id=document_id, topic=concept), default_chars=3000)

    prompt = (
        f"Explain the concept '{concept}' to a complete beginner in very simple language. "
        'Respond in JSON with keys "explanation" (2-4 simple sentences, no jargon) and '
        '"analogy" (one everyday analogy).'
    )
    if context:
        prompt += f"\n\nUse this context if relevant:\n{context[:3000]}"

    raw = await call_llm(
        [
            {"role": "system", "content": "You explain things simply, like to a 12-year-old. Output valid JSON only."},
            {"role": "user", "content": prompt},
        ],
        force_json=True,
    )
    data = parse_json(raw)
    if data and data.get("explanation"):
        return ExplainSimpleResponse(
            concept=concept,
            explanation=str(data["explanation"]).strip(),
            analogy=(str(data["analogy"]).strip() if data.get("analogy") else None),
            used_llm=True,
        )

    if context:
        sents = _sentences(context)
        expl = " ".join(sents[:2]) if sents else f"'{concept}' appears in your notes, but I need an LLM key to simplify it."
    else:
        expl = (
            f"I couldn't find '{concept}' in your notes. Connect an OPENAI_API_KEY to get a "
            "beginner-friendly explanation from general knowledge."
        )
    return ExplainSimpleResponse(concept=concept, explanation=expl, analogy=None, used_llm=False)


# --------------------------------------------------------------------------- #
# 5. Exam Revision Mode
# --------------------------------------------------------------------------- #
async def revision_mode(req: StudyToolRequest) -> RevisionResponse:
    content, source = _content_for(req)
    title = f"Revision sheet: {source or req.topic or 'your notes'}"

    prompt = (
        "Create a last-minute exam revision sheet from the material below. "
        "Respond in JSON with keys: "
        '"quick_notes" (6-10 punchy bullet strings of the most important facts), '
        '"key_formulas" (array of formula strings, empty if none), and '
        '"must_know" (3-5 critical things to remember).\n\n'
        f"MATERIAL:\n{content[:7000]}"
    )
    raw = await call_llm(
        [
            {"role": "system", "content": "You create concise exam revision sheets. Output valid JSON only."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=900,
        force_json=True,
    )
    data = parse_json(raw)
    if data and (data.get("quick_notes") or data.get("must_know")):
        return RevisionResponse(
            title=title,
            quick_notes=[str(x).strip() for x in data.get("quick_notes", [])][:10],
            key_formulas=[str(x).strip() for x in data.get("key_formulas", [])][:10],
            must_know=[str(x).strip() for x in data.get("must_know", [])][:5],
            used_llm=True,
            source=source,
        )

    # Fallback: key sentences + substrings that look like formulas (e.g. KE = 0.5 * m * v^2)
    sents = _sentences(content)
    formula_re = re.compile(
        r"[A-Za-z]{1,6}\s*=\s*[0-9A-Za-z.^*/+\-() ]+?(?=\.\s|\.$|[;,]|$)"
    )
    formulas: list[str] = []
    for m in formula_re.finditer(content):
        f = m.group().strip().rstrip(".")
        if f and f not in formulas:
            formulas.append(f)
        if len(formulas) >= 6:
            break
    return RevisionResponse(
        title=title,
        quick_notes=[s[:140] for s in sents[:8]],
        key_formulas=formulas,
        must_know=[s[:120] for s in sents[:3]],
        used_llm=False,
        source=source,
    )
