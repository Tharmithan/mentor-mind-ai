# Week 5 · Day 3 — AI Answer Evaluation

Evaluates interview answers on communication, relevance, technical depth, and confidence.

## Metrics (0–100)

| Field | Description |
|-------|-------------|
| `communication` | Clarity + grammar blend |
| `technical_score` | Relevance, keywords, semantic match |
| `confidence` | Hedging / assertiveness heuristics |
| `relevance` | On-topic vs question |
| `grammar` | Punctuation, filler words, sentence shape |
| `clarity` | Structure and readability |
| `keyword_match` | Expected terms from question bank |
| `semantic_similarity` | SentenceTransformer cosine vs ideal answer |
| `answer_length` | Word count proxy |
| `overall` | Average of core dimensions |

## Ideal answer comparison

Each question can define in `questions.json`:

- `expected_keywords` — terms to mention
- `ideal_answer` — expert outline for semantic similarity

Response field `ideal_comparison`:

```json
{
  "expert_answer": "...",
  "expected_keywords": ["LIFO", "FIFO"],
  "matched_keywords": ["stack", "LIFO"],
  "missing_keywords": ["FIFO", "queue"],
  "similarity_pct": 72.5
}
```

## Technologies

- **Heuristics** — `analyzer.py` (0–10 base scores)
- **SentenceTransformers** — RAG embedder (`app/rag/embeddings.py`) for semantic similarity
- **Optional LLM** — `OPENAI_API_KEY` → structured JSON scores + expert paragraph

## API

`POST /api/interview/session/{id}/answer`

```json
{
  "answer_text": "A stack is LIFO used for undo...",
  "transcript": "optional speech transcript"
}
```

Turn feedback includes `scores`, `ideal_comparison`, and `used_llm`.

## Example scores block

```json
{
  "communication": 84,
  "technical_score": 78,
  "confidence": 81,
  "relevance": 80,
  "grammar": 75,
  "clarity": 82,
  "keyword_match": 67,
  "semantic_similarity": 71,
  "answer_length": 55,
  "overall": 80
}
```
