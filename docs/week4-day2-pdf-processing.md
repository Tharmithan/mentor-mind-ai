# Week 4 · Day 2 — PDF Processing System

**Goal:** Let users upload learning materials (PDFs), extract the text, and split it
into chunks ready for embedding/retrieval in the RAG pipeline.

---

## Pipeline

```
upload  ──►  save to backend/uploads/  ──►  extract text (PyPDFLoader)
        ──►  split into chunks (RecursiveCharacterTextSplitter)
        ──►  persist chunks JSON to backend/uploads/processed/
```

---

## Chunking strategy (IMPORTANT)

Chunking quality makes or breaks retrieval. We use the recommended config:

```python
chunk_size = 500       # characters per chunk
chunk_overlap = 50     # characters shared between adjacent chunks
```

- **chunk_size 500** — small enough to be a focused, retrievable idea; big enough to
  keep meaning.
- **chunk_overlap 50** — carries a little context across boundaries so an idea split
  between two chunks isn't lost.

The splitter tries natural boundaries first (`\n\n`, `\n`, `. `, ` `) before cutting
mid-word.

---

## Libraries

| Purpose | Library |
|---------|---------|
| Extract PDF text | `langchain_community.document_loaders.PyPDFLoader` (uses `pypdf`) |
| Chunk text | `langchain_text_splitters.RecursiveCharacterTextSplitter` |

---

## Backend structure

```
backend/
├── uploads/                     # raw uploaded files (gitignored)
│   └── processed/               # {document_id}.json  (meta + chunks)
└── app/
    ├── rag/
    │   ├── pdf_processor.py      # extract text + split into chunks
    │   └── document_service.py   # save file, process, persist, list, delete
    ├── models/document.py        # Pydantic models
    └── routes/documents.py       # API routes
```

Uploaded files and processed chunks are **gitignored** (only the folder structure is
tracked via `.gitkeep`).

---

## API

| Method | Route | Description |
|--------|-------|-------------|
| `POST` | `/api/documents/upload` | Upload a PDF/TXT/MD → extract + chunk |
| `GET` | `/api/documents` | List processed documents (newest first) |
| `GET` | `/api/documents/{id}/chunks` | All chunks for a document |
| `DELETE` | `/api/documents/{id}` | Delete a document + its chunks |

### Upload response (shape)

```json
{
  "message": "Processed 'study_notes.pdf' into 10 chunks.",
  "document": {
    "document_id": "94cb3d11dfcd",
    "filename": "study_notes.pdf",
    "uploaded_at": "2026-05-29T07:12:00+00:00",
    "num_pages": 2,
    "num_chunks": 10,
    "total_chars": 3892,
    "chunk_size": 500,
    "chunk_overlap": 50
  },
  "preview_chunks": [ { "chunk_id": "94cb3d11dfcd_0", "page": 1, "text": "..." } ]
}
```

Limits: max upload size **25 MB**; allowed types `.pdf`, `.txt`, `.md`.

---

## Try it

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload

# in another shell
curl -F "file=@notes.pdf" http://localhost:8000/api/documents/upload
curl http://localhost:8000/api/documents
```

---

## Checklist

- [x] `backend/uploads/` created (gitignored, structure kept)
- [x] PDF upload API (`POST /api/documents/upload`)
- [x] Extract PDF text (`PyPDFLoader`)
- [x] Chunk large text (`RecursiveCharacterTextSplitter`, 500/50)
- [x] Save processed chunks (`uploads/processed/{id}.json`)
- [x] Smoke-tested end-to-end (2-page PDF → 10 chunks, all ≤ 500 chars)

---

## Next (Day 3)

Embed the stored chunks and index them in a vector database, then add a `/rag/ask`
endpoint that retrieves the relevant chunks and answers questions about the document.
