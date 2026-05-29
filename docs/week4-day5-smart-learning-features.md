# Week 4 · Day 5 — Smart Learning Features

Make the AI feel intelligent. Five tools that turn uploaded notes into study aids,
all built on the Day 1-4 RAG stack.

| Feature | What it does |
|---------|--------------|
| **AI Summarizer** | Summary paragraph + key points of a document |
| **Quiz Generator** | Auto-generated multiple-choice questions |
| **Flashcard Generator** | Front/back revision cards |
| **Explain Like a Beginner** | Simplifies a concept (+ everyday analogy) |
| **Exam Revision Mode** | Last-minute notes, quick sheet, key formulas |

Every tool uses the LLM when `OPENAI_API_KEY` is set, and a sensible **extractive
fallback** otherwise — so the whole feature set works offline (just less polished).

---

## Backend

### Reusable LLM layer — `app/rag/llm.py`
- `call_llm(messages, …, force_json=True)` — generic OpenAI-compatible call (JSON mode).
- `parse_json()` — tolerant JSON parser (handles markdown code fences).
- `llm_enabled()` — whether a key is configured.

### Generators — `app/rag/study_tools.py`
Each gathers content from a document (`DocumentService.get_text`) and/or
semantically-retrieved chunks, prompts the LLM for **structured JSON**, validates it,
and falls back to heuristics:

| Tool | LLM output | Fallback |
|------|-----------|----------|
| `summarize` | summary + key_points | first sentences of the notes |
| `generate_quiz` | MCQs (4 options + answer) | fill-in-the-keyword questions |
| `generate_flashcards` | front/back cards | "X is Y" → Q/A pairs |
| `explain_simple` | simple explanation + analogy | relevant chunk text |
| `revision_mode` | quick_notes / formulas / must_know | key sentences + regex-extracted formulas (e.g. `KE = 0.5 * m * v^2`) |

### Routes — `POST /api/study/*`

```
/api/study/summarize    { document_id?, topic?, count? }
/api/study/quiz         { document_id?, topic?, count? }
/api/study/flashcards   { document_id?, topic?, count? }
/api/study/explain      { concept, document_id? }
/api/study/revision     { document_id?, topic?, count? }
/api/study/status       -> { llm_enabled }
```

`summarize/quiz/flashcards/revision` require a `document_id` and/or `topic`; `explain`
works from general knowledge if the concept isn't in the notes.

---

## Frontend — `/assistant`

The assistant page is now a **workspace** with a shared document sidebar and two tabs:

- **Chat** — the Day 4 RAG tutor (`ChatPanel`).
- **Study Tools** — `StudyToolsPanel`: pick a tool, hit Generate, view results.

Component split: `AssistantWorkspace` (state + tabs) → `DocumentsPanel`, `ChatPanel`,
`StudyToolsPanel`.

### UI per tool
- **Summarize** — paragraph + bullet key points.
- **Quiz** — interactive MCQs; click an option to reveal correct/incorrect + explanation.
- **Flashcards** — tap-to-flip cards in a grid.
- **Explain simply** — concept input → explanation + highlighted analogy.
- **Exam Revision** — quick notes, formula chips, and a "must know" list.

Each result shows an **AI-generated** vs **Extractive** badge so it's clear which path ran.

---

## Verified

- Backend smoke test (no LLM key): all five tools return valid, schema-correct payloads;
  quiz answer indices in range; revision formula extraction yields `F = ma`,
  `KE = 0.5 * m * v^2`; no-source request → 400.
- `next build` passes TypeScript; `/assistant` prerenders.
- Routes registered: `summarize`, `quiz`, `flashcards`, `explain`, `revision`, `status`.

---

## Checklist

- [x] AI Summarizer
- [x] Quiz Generator (MCQs)
- [x] Flashcard Generator
- [x] Explain Like a Beginner
- [x] Exam Revision Mode (notes, quick sheet, formulas)

---

## Next

Persist generated quizzes/flashcards per document, spaced-repetition scheduling, and
export to PDF.
