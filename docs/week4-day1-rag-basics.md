# Week 4 · Day 1 — Learn RAG Basics

**Goal:** Make the AI answer questions based on **uploaded documents** (notes, PDFs,
syllabus) instead of only its own training data.

RAG = **Retrieval Augmented Generation**.

---

## Why RAG?

A plain LLM only knows what it was trained on. It cannot answer:

> "What does *my* chapter-5 notes say about photosynthesis?"

RAG fixes this by **retrieving** the relevant pieces of *your* documents first, then
asking the LLM to answer **using that retrieved context**. This means:

- Answers are grounded in your real material (less hallucination).
- You can update knowledge by adding documents — no re-training.
- Perfect for MentorMind: "ask questions about your own study notes".

---

## The 4 Core Concepts

### 1. Embeddings — text → vectors

An **embedding** turns a piece of text into a list of numbers (a vector) that captures
its *meaning*. Sentences with similar meaning end up close together in vector space.

```
"I love algebra"      → [0.12, -0.04, 0.88, ...]   (384 numbers)
"Maths is fun"        → [0.10, -0.02, 0.85, ...]   ← close vector = similar meaning
"The cat slept"       → [-0.55, 0.71, 0.03, ...]   ← far vector  = different meaning
```

We use **SentenceTransformers** (`all-MiniLM-L6-v2`, 384 dims) — small, fast, runs locally.

### 2. Vector Database — store embeddings

Once every document chunk is an embedding, we store them in a **vector database** so we
can search by *meaning* quickly. We use **ChromaDB** (simple, local, persists to disk).
FAISS is the alternative (faster at huge scale, but no built-in storage layer).

### 3. Semantic Search — find relevant chunks

When the user asks a question, we embed the **question** too, then ask the vector DB:

> "Give me the chunks whose vectors are closest to this question's vector."

This is **semantic** (meaning-based), not keyword matching — "exam stress" can match a
chunk about "test anxiety" even with zero shared words.

### 4. LLM Response Generation — generate the answer

We stuff the top retrieved chunks into a prompt:

```
Use ONLY the context below to answer.
Context:
<retrieved chunks>

Question: <user question>
```

The LLM then writes a grounded, natural-language answer.

---

## RAG Architecture (end to end)

```
                       ┌─────────────────── INDEXING (once per document) ───────────────────┐
                       │                                                                     │
 upload.pdf  ──►  Load (pypdf)  ──►  Split into chunks  ──►  Embed (SentenceTransformers)  ──►  Store (ChromaDB)
                       │                                                                     │
                       └─────────────────────────────────────────────────────────────────────┘

                       ┌──────────────────────── QUERY (every question) ─────────────────────┐
                       │                                                                      │
 question  ──►  Embed question  ──►  Semantic search in ChromaDB  ──►  top-k chunks           │
                       │                                                       │              │
                       │                                                       ▼              │
                       │                            Build prompt (chunks + question)          │
                       │                                                       │              │
                       │                                                       ▼              │
                       │                                   LLM  ──►  grounded answer          │
                       └──────────────────────────────────────────────────────────────────────┘
```

| Stage | Tool | What it does |
|-------|------|--------------|
| Load | `pypdf` | Read text out of PDFs |
| Split | LangChain `RecursiveCharacterTextSplitter` | Break long text into ~500-char chunks with overlap |
| Embed | `sentence-transformers` (`all-MiniLM-L6-v2`) | text → 384-dim vectors |
| Store / Search | `chromadb` | Persist vectors + nearest-neighbour search |
| Generate | LLM (OpenAI-compatible, optional) | Write the final answer from retrieved context |

---

## Install

```bash
cd backend
source .venv/bin/activate
pip install -r requirements-rag.txt
# or:
pip install langchain langchain-community chromadb sentence-transformers pypdf
```

> These pull in `torch`, so the download is large. They live in **`requirements-rag.txt`**
> (separate from the main `requirements.txt`) so the core API stays lightweight.

---

## Testing notebook

`notebooks/07_rag_basics.ipynb` walks through every concept hands-on:

1. Create embeddings and **see** semantic similarity in action.
2. Build a ChromaDB collection from sample study notes.
3. Run semantic search and inspect the retrieved chunks.
4. (Optional) Generate a final answer with an LLM if `OPENAI_API_KEY` is set.

No PDF or API key required — it ships with built-in sample notes so it runs end-to-end
offline (the LLM step is the only part that needs a key).

---

## Checklist

- [x] Learn RAG architecture (this doc)
- [x] Install libraries (`requirements-rag.txt`)
- [x] Create testing notebook (`07_rag_basics.ipynb`)

---

## Next (Day 2)

Wire RAG into the backend: a `/rag/upload` endpoint to index documents and a `/rag/ask`
endpoint to answer questions about them.
