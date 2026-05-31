# Week 8 · Day 4 — Performance Optimization

Make the app fast — measure latency, cache hot paths, and defer heavy bundles.

---

## What was optimized

| Layer | Change | Impact |
|-------|--------|--------|
| **Backend ML** | SHAP `TreeExplainer` cache + model warmup on startup | Faster `/predict/explain`, no cold-start on first request |
| **Backend async** | `asyncio.to_thread()` for predict, upload, search | CPU work no longer blocks the event loop |
| **AI responses** | TTL cache on `/insights`, `/ai/status`, `/explain/global` | Repeat reads skip recomputation |
| **Vector DB** | LRU cache for query embeddings (256 entries) | Faster repeat RAG searches |
| **RAG docs** | Document list cache (mtime invalidation) | Faster `GET /documents` |
| **LLM** | Shared `httpx.AsyncClient` connection pool | Lower LLM call overhead |
| **Database** | Indexes on `user_id` FK columns | Faster user-scoped queries |
| **Observability** | `X-Response-Time` header + `GET /api/metrics/latency` | Measure API latency per route |
| **Frontend** | Lazy-loaded panels, interview coach, floating assistant | Smaller initial JS bundle |
| **Frontend cache** | `queryCache.ts` TTL cache for dashboard, coach, tips | Fewer duplicate API calls |
| **Images** | `next.config.ts` AVIF/WebP formats (ready for future assets) | Optimized when images are added |

---

## Measure API latency

```bash
chmod +x scripts/benchmark-api.sh
./scripts/benchmark-api.sh http://127.0.0.1:8000 5
```

Each response includes `X-Response-Time: 12.3ms`.

Server-side aggregates:

```bash
curl http://127.0.0.1:8000/api/metrics/latency | python3 -m json.tool
```

---

## Backend details

### Model warmup (`app/main.py`)

On startup, predictor, explainer, and embedder load in a background thread so the first user request is not penalized.

### SHAP cache (`app/ai/explainer.py`)

`TreeExplainer` instances are keyed by model `id()` and reused across `/predict/explain` calls.

### Response cache (`app/core/cache.py`)

```python
@ttl_cache(ttl_seconds=120, prefix="insights")
async def insights(...):
```

### Thread offload

- `PredictionService.predict_performance` → `asyncio.to_thread(get_predictor().predict, ...)`
- Document upload/search → `asyncio.to_thread(DocumentService.*, ...)`

---

## Frontend details

### Lazy loading

Heavy components load on demand via `next/dynamic`:

- `FloatingAIAssistant` (global)
- Dashboard panels: `AnalyticsDashboard`, `MLPredictPanel`, etc.
- Coach panels: `MLOpsPanel`, `MonitoringPanel`, etc.
- `InterviewCoach` (MediaPipe deferred until route visit)
- Assistant: `ChatPanel`, `StudyToolsPanel`

### Client cache (`src/lib/queryCache.ts`)

```typescript
cachedFetch("dashboard", getDashboard, 5 * 60_000);
cachedFetch("daily-tip", getDailyTip, 24 * 60_000);
```

---

## Database indexes

Added to ORM models (applied on next `create_tables` or migration):

- `ix_performance_data_user_id`
- `ix_recommendations_user_id`
- `ix_interview_results_user_id`
- `ix_refresh_tokens_user_id`

---

## Quick verify

```bash
# Backend tests still pass
cd backend && pytest -v

# Benchmark (backend must be running)
./scripts/benchmark-api.sh

# Frontend build
cd frontend && npm run build
```

---

## Next steps (optional)

- Redis for distributed response cache in production
- React Query for richer cache invalidation
- Consolidate chart.js → recharts to shrink bundle further
- `uvicorn --workers 2` on Railway for parallel ML requests
