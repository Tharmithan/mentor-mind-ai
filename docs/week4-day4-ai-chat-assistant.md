# Week 4 · Day 4 — AI Chat Assistant (the WOW feature)

**Goal:** an AI tutor chatbot that answers from the student's uploaded notes —
explains concepts, summarizes topics, and gives examples.

This closes the full **RAG loop**:

```
User Question
      ↓
Semantic Search   (Day 3 — ChromaDB + all-MiniLM-L6-v2)
      ↓
Relevant Chunks
      ↓
LLM               (OpenAI-compatible, with offline fallback)
      ↓
AI Response  (+ the source chunks it used)
```

---

## Backend

### LLM answer generation — `app/rag/llm.py`

- `generate_answer(question, chunks, history, mode)` builds a grounded prompt from the
  retrieved chunks and calls an **OpenAI-compatible** chat API.
- Configurable via env: `OPENAI_API_KEY`, `OPENAI_BASE_URL` (default OpenAI),
  `OPENAI_MODEL` (default `gpt-4o-mini`). Works with OpenAI, Mistral, Groq/Llama 3,
  Google AI Studio (OpenAI-compatible endpoint), etc.
- **Offline fallback:** with no key (or on any LLM error) it returns an *extractive*
  answer built from the top chunk(s), so the assistant is always usable.
- **Modes** tune the system prompt: `explain`, `summarize`, `example`.
- Short conversation `history` is included for multi-turn context.

### Chat endpoint — `POST /api/documents/chat`

```jsonc
// request
{
  "question": "Explain recursion",
  "top_k": 4,
  "document_id": null,        // optional — scope to one document
  "mode": "explain",          // optional
  "history": [{ "role": "user", "content": "..." }]
}
// response
{
  "answer": "Recursion is when a function calls itself…",
  "used_llm": true,
  "model": "gpt-4o-mini",
  "sources": [ { "filename": "lecture.pdf", "page": 1, "similarity": 0.77, "text": "…" } ]
}
```

`DocumentService.chat()` runs search → LLM and returns the answer plus the source chunks
so the UI can show *where* the answer came from.

---

## Frontend

| File | Purpose |
|------|---------|
| `app/assistant/page.tsx` + `layout.tsx` | New `/assistant` route (dashboard shell) |
| `components/assistant/ChatAssistant.tsx` | Upload + document list + chat UI |
| `lib/api.ts` | `uploadDocument`, `listDocuments`, `deleteDocument`, `chatWithDocuments` |
| `lib/types/api.ts` | Document + chat types |
| `Sidebar` / `MobileNav` | "AI Study Assistant" nav entry (now live) |

### Chat UI features

- **Upload** PDF/TXT/MD (drag-free click), with processing state.
- **Document list** with per-doc selection (scope chat to one doc) or "All documents",
  plus delete.
- **Chat thread** with user/assistant bubbles and auto-scroll.
- **Quick modes**: Explain · Summarize · Examples.
- **Sources** are collapsible under each answer, showing filename, page, and % match.
- Graceful states: backend offline, no LLM key (shows "extractive answer" note).

---

## Suggested models

| Type | Option | How |
|------|--------|-----|
| API | OpenAI | `OPENAI_API_KEY` (default base URL) |
| API | Google AI Studio | set `OPENAI_BASE_URL` to its OpenAI-compatible endpoint |
| Open source | Mistral / Llama 3 | point `OPENAI_BASE_URL` at Groq / Ollama / vLLM |

No key? The extractive fallback keeps the demo working.

---

## Verified

- Backend smoke test: upload → chat returns a grounded answer + 2 sources
  (top source 0.76 match for "Explain recursion"); unrelated question handled.
- `next build` passes TypeScript with the new `/assistant` route prerendered.
- All document routes registered: `upload`, `search`, `chat`, list, chunks, delete.

---

## Checklist

- [x] Build chatbot UI
- [x] Connect backend (`/api/documents/chat`)
- [x] Retrieve relevant chunks (semantic search)
- [x] Generate responses (LLM + offline fallback)

---

## Next

Streaming responses, citations inline in the answer, and multi-document study sessions.
