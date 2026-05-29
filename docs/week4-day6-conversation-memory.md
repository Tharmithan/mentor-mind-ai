# Week 4 · Day 6 — Conversation Memory

Make the chatbot feel advanced: it **remembers the conversation** so follow-ups work.

```
User: "Explain CNN."        ->  AI explains CNNs
User: "Give an example."    ->  AI knows you mean "an example of a CNN"
```

---

## How it works

Each chat runs inside a **session** with server-side memory:

```
question + session_id
      ↓
recall session history + last topic + last document   (memory)
      ↓
context-aware semantic search   (folds prior topic into vague follow-ups)
      ↓
LLM with full conversation history
      ↓
answer  ->  appended back into the session
```

### Memory system — `app/rag/memory.py`

- Built on LangChain's **`InMemoryChatMessageHistory`** (the ConversationBufferMemory
  primitive) — one buffer per session.
- Tracks **previous learning context**: the recent user questions (`topics`) and the
  `last_document_id` the session has been studying.
- **Persists** each session to `backend/uploads/sessions/{id}.json` (gitignored) so a
  conversation survives a restart.
- Buffer is windowed (last ~20 turns) to keep prompts bounded.

### Context-aware retrieval — `DocumentService._retrieval_query`

A short/vague follow-up ("give an example", "why?", "explain more") is detected and the
**previous topic is folded into the search query**, and the session's remembered
document is used when none is supplied. That's why *"Give an example"* still retrieves
CNN chunks rather than something unrelated.

---

## API

| Method | Route | Description |
|--------|-------|-------------|
| `POST` | `/api/chat/sessions` | Start a conversation → `session_id` |
| `GET` | `/api/chat/sessions/{id}` | Fetch history + learning context |
| `DELETE` | `/api/chat/sessions/{id}` | Forget the conversation |

`POST /api/documents/chat` now accepts a `session_id` (and echoes it back). With a
session, the client no longer needs to send history — the server remembers it. A
`history` array is still accepted as a fallback for sessionless calls.

---

## Frontend

`ChatPanel` now:
- Starts a memory-backed session on mount (best-effort; chat still works offline).
- Sends `session_id` with every message and adopts the one returned by the server.
- Shows a **"Memory on — I remember this chat"** indicator.
- Has a **New chat** button that forgets the old session and starts a fresh one.

---

## Verified

Backend smoke test:
- Turn 1 *"Explain CNN"* → retrieves the CNN passage.
- Turn 2 *"Give an example"* with **no document_id and no topic word** → still retrieves
  CNN content (resolved via remembered document + previous topic).
- Session stored 4 messages (2 user + 2 assistant) and tracked `last_document_id`.
- Delete → subsequent fetch returns 404.

`next build` passes TypeScript; `/assistant` prerenders.

---

## Checklist

- [x] Chat history (per-session buffer)
- [x] Memory system (LangChain `InMemoryChatMessageHistory` + persistence)
- [x] Previous learning context (recent topics + last document)
- [x] Follow-ups resolve automatically (CNN → "give example")

---

## Next

Long-term memory (summarized older turns), per-user session lists, and a memory recall
panel in the UI.
