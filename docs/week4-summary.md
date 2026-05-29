# Week 4 Summary — RAG, AI Tutor & Smart Learning

Week 4 turned MentorMind into a genuine **AI study companion**: upload your notes and
the AI answers, summarizes, quizzes, and remembers — a full Retrieval-Augmented
Generation (RAG) system end to end.

---

## What was built, day by day

| Day | Feature | Key pieces |
|-----|---------|-----------|
| 1 | RAG basics | `requirements-rag.txt`, testing notebook, architecture doc |
| 2 | PDF processing | upload → extract (PyPDFLoader) → chunk (500/50) → persist |
| 3 | Embeddings + vector DB | `all-MiniLM-L6-v2` + ChromaDB + semantic search |
| 4 | AI chat assistant | full RAG loop, `/api/documents/chat`, `/assistant` UI |
| 5 | Smart learning features | summarizer, quiz, flashcards, ELI5, exam revision |
| 6 | Conversation memory | sessions, LangChain buffer, follow-up resolution |
| 7 | UI + AI experience | markdown, code blocks, typewriter, thinking animation, suggestions |

---

## Week 4 output — achieved

**AI features**
- ✔ RAG pipeline (PDF → chunks → embeddings → vector DB → LLM)
- ✔ PDF upload
- ✔ AI chatbot (grounded, with memory)
- ✔ Semantic search
- ✔ AI summaries
- ✔ Quiz generation (+ flashcards, ELI5, revision mode)

**Backend**
- ✔ Embeddings API (`all-MiniLM-L6-v2`)
- ✔ Vector search API (ChromaDB, cosine)

**Frontend**
- ✔ Modern chat UI (markdown, streaming, thinking animation, suggestions)
- ✔ PDF upload UI + study tools

---

## Architecture

```
                ┌──────────────── INDEXING (on upload) ─────────────────┐
 upload.pdf ──► PyPDFLoader ──► chunk(500/50) ──► all-MiniLM-L6-v2 ──► ChromaDB
                └────────────────────────────────────────────────────────┘

                ┌──────────────── QUERY (chat / tools) ─────────────────┐
 question ─► (+ memory: prior topic & doc) ─► semantic search ─► top chunks
                                                                  │
                                                                  ▼
                                          LLM (OpenAI-compatible) ──► answer + sources
                └────────────────────────────────────────────────────────┘
```

`backend/app/rag/`: `pdf_processor`, `embeddings`, `vector_store`, `document_service`,
`llm`, `study_tools`, `memory`.

---

## API surface (Week 4)

```
POST   /api/documents/upload          upload + extract + chunk + index
GET    /api/documents                 list documents
GET    /api/documents/{id}/chunks     chunks for a document
DELETE /api/documents/{id}            delete document (+ vectors)
POST   /api/documents/search          semantic search
POST   /api/documents/chat            RAG chat (+ session memory)

POST   /api/study/summarize|quiz|flashcards|explain|revision
GET    /api/study/status

POST   /api/chat/sessions             start a conversation
GET    /api/chat/sessions/{id}        history + learning context
DELETE /api/chat/sessions/{id}        forget conversation
```

---

## Learning goals — covered

RAG systems · embeddings · vector databases · semantic search · LLM integration ·
conversational AI.

---

## Design notes

- **Works offline.** Every LLM feature has an extractive fallback, so the whole app is
  demoable without an API key. Set `OPENAI_API_KEY` (+ optional `OPENAI_BASE_URL` /
  `OPENAI_MODEL`) for full AI quality — compatible with OpenAI, Google AI Studio, and
  open-source models (Mistral, Llama 3 via Groq/Ollama).
- **Multi-PDF intelligence** is built in: leave a document unselected to search across
  all uploaded documents.
- **Citations** are shown on every answer (filename · page · % match).
- Uploaded files, vector store, and sessions are gitignored; only structure is tracked.

---

## Ideas for later

Personalized tutor (adapt to weak subjects / performance), long-term memory
summarization, real server-side token streaming (SSE), and a daily AI study companion
with goals + revision reminders.
