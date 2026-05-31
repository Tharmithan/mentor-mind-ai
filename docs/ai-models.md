# MentorMind AI — AI Models Reference

> Catalog of machine learning models, LLM integrations, embeddings, and agents used in production.

---

## 1. Overview

| Category | Technology | Location |
|----------|------------|----------|
| **Tabular ML** | Random Forest, XGBoost (joblib) | `ml-models/` |
| **Explainability** | SHAP | `backend/app/ai/explainer.py` |
| **LLM** | OpenAI GPT-4o-mini (optional) | `backend/app/rag/llm.py` |
| **Embeddings** | sentence-transformers | `backend/app/rag/embeddings.py` |
| **Vector search** | ChromaDB | `backend/uploads/vectorstore/` |
| **Agents** | Rule + LLM hybrid | `backend/app/agents/` |
| **MLOps** | MLflow + JSON registry | `ml-models/mlops/` |

---

## 2. Student Performance Models

### 2.1 Production configuration

Defined in `ml-models/best_model.json`:

```json
{
  "score_model": "random_forest",
  "score_file": "saved_models/performance_model_v2.joblib",
  "pass_model": "random_forest",
  "pass_file": "saved_models/pass_fail_model_v2.joblib",
  "version": "v2"
}
```

Promote alternate versions via `POST /api/mlops/models/promote`.

### 2.2 Model versions

| Version | Algorithm | Artifacts | Notes |
|---------|-----------|-----------|-------|
| **v2** | Random Forest | `performance_model_v2.joblib`, `pass_fail_model_v2.joblib` | Current production |
| **v3** | XGBoost (tuned) | `performance_model_v3.joblib`, `pass_fail_model_v3.joblib` | Higher F1 on holdout |

Manifests: `ml-models/saved_models/model_manifest*.json`

### 2.3 Input features (8)

| Feature | Source |
|---------|--------|
| `study_hours` | User input |
| `attendance_pct` | User input |
| `past_failures` | Derived from quiz completion |
| `assignment_completion_score` | Engineered |
| `exam_readiness_score` | Engineered |
| `productivity_index` | Engineered |
| `consistency_score` | Prior score proxy |
| `wellness_score` | Sleep hours → 1–5 scale |

Feature engineering: `datasets/scripts/ml_features.py`

### 2.4 Outputs

| Model | Target | Output |
|-------|--------|--------|
| **Regression** | `performance_pct` | Predicted score 0–100 |
| **Classification** | `at_risk` | Pass/fail probability |

API response includes: `prediction`, `confidence`, `predicted_score`, `risk_level`, `student_risk`, `monitoring_log_id`.

### 2.5 Training metrics

See `ml-models/training_metrics.json`:

| Algorithm | Regression R² | Classification F1 |
|-----------|---------------|-------------------|
| Random Forest | 0.009 | 0.626 |
| XGBoost | -0.037 | 0.588 |

Training script: `datasets/scripts/train_models.py`  
MLOps wrapper: `datasets/scripts/mlops_experiment.py`

### 2.6 Explainability (SHAP)

- **Endpoint:** `POST /api/predict/explain`
- **Method:** TreeExplainer on loaded joblib bundle
- **Output:** Feature contributions, top driver, natural language summary

---

## 3. Recommendation Engine

| Component | Type | Description |
|-----------|------|-------------|
| **Rule engine** | Heuristic | Weak-topic → resource mapping |
| **Personalization** | Style-aware | Filters by video/reading/interactive/hands-on |
| **Feedback loop** | Continuous | Downranks poorly rated resources |

Modules: `backend/app/recommendation/`, `backend/app/personalization/recommender.py`

---

## 4. LLM Integrations (Optional)

Requires `OPENAI_API_KEY` in `backend/.env`.

| Use case | Module | Model default |
|----------|--------|---------------|
| RAG chat | `rag/llm.py` | gpt-4o-mini |
| Interview feedback | `interview/feedback_generator.py` | gpt-4o-mini |
| AI insights | `ai/llm_insights.py` | gpt-4o-mini |
| Study tools | `rag/study_tools.py` | gpt-4o-mini |
| Agent responses | `agents/*` | gpt-4o-mini |

**Fallback:** Heuristic responses when API key is absent.

---

## 5. Embeddings & RAG

| Component | Model | Dimensions |
|-----------|-------|------------|
| Document embeddings | `all-MiniLM-L6-v2` | 384 |
| User profile embeddings | Same model | 384 |

**Pipeline:**
```
PDF → PyPDF extract → 512-token chunks → embed → ChromaDB (cosine)
Query → embed → top-k retrieval → LLM prompt with context
```

---

## 6. Interview AI

| Component | Method |
|-----------|--------|
| Answer scoring | Heuristic + optional LLM |
| Turn feedback | `feedback_generator.py` |
| Speech-to-text | Whisper (optional) |
| Emotion | FER + client-side MediaPipe metrics |
| Coach report | Aggregated session summary |

---

## 7. Multi-Agent System

| Agent | Handler | Capabilities |
|-------|---------|--------------|
| Study | `study_agent.py` | Plans, goals, daily recs |
| Interview | `interview_agent.py` | Prep coaching |
| Career | `career_agent.py` | Paths, gaps, roadmaps |
| Resume | `resume_agent.py` | ATS analysis |

**Router:** Keyword + regex intent classification (`agents/router.py`)  
**Collaboration:** Orchestrator chains agents for complex queries (`agents/collaboration/`)

---

## 8. Model Monitoring

Every `/api/predict` call is logged to `uploads/monitoring/prediction_logs.json`.

| Metric | Description |
|--------|-------------|
| MAE | Mean absolute error when user submits actual score |
| Drift status | `stable` · `watch` · `alert` |
| Feedback rating | User thumbs up/down on predictions |

Endpoint: `GET /api/monitoring/model-metrics`

---

## 9. Artifact Layout

```
ml-models/
├── best_model.json              # Production pointer
├── training_metrics.json        # Last training run metrics
├── saved_models/
│   ├── performance_model_v2.joblib
│   ├── pass_fail_model_v2.joblib
│   ├── performance_model_v3.joblib
│   ├── pass_fail_model_v3.joblib
│   └── model_manifest*.json
├── mlops/
│   ├── registry.json
│   ├── experiments.json
│   └── deployments.json
└── mlflow/                      # MLflow runs (optional)
```

---

## 10. Retraining

```bash
# Full training
python datasets/scripts/train_models.py

# MLOps experiment with MLflow
python datasets/scripts/mlops_experiment.py --algorithm both --mlflow

# Promote to production
curl -X POST http://localhost:8000/api/mlops/models/promote \
  -H "Content-Type: application/json" \
  -d '{"version": "v3"}'
```

See [week7-day5-mlops-pipeline.md](./week7-day5-mlops-pipeline.md).
