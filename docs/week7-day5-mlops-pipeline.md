# Week 7 · Day 5 — MLOps Pipeline

Model versioning, experiment tracking, and deployment for MentorMind AI student performance models.

## What you built

| Capability | Implementation |
|------------|----------------|
| **Model version tracking** | `ModelRegistry` scans `ml-models/saved_models/` manifests + joblib artifacts |
| **Training logs** | JSON logs in `ml-models/training/logs/` + optional MLflow runs |
| **Experiment comparison** | Compare R² / F1 across v2, v3, and new runs |
| **Deployment pipeline** | Promote version → update `best_model.json` → hot-reload `MLPredictor` |

## Stack

- **Git** — each registry entry stores `git rev-parse --short HEAD`
- **Docker** — `docker-compose.mlops.yml` (API + MLflow tracking server)
- **MLflow** — optional; falls back to JSON store when not installed

## Quick start

### 1. API (no MLflow)

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Open **Coach dashboard** → **MLOps Pipeline** panel, or hit:

```bash
curl http://localhost:8000/api/mlops/status
curl http://localhost:8000/api/mlops/models
curl http://localhost:8000/api/mlops/experiments/compare
```

### 2. Install MLflow (optional)

```bash
pip install -r backend/requirements-mlops.txt
```

Set in `.env`:

```
MLFLOW_TRACKING_URI=file:../ml-models/mlflow/mlruns
```

### 3. Run a training experiment

```bash
python datasets/scripts/mlops_experiment.py --algorithm both --mlflow
```

Or via API:

```bash
curl -X POST http://localhost:8000/api/mlops/experiments/run \
  -H "Content-Type: application/json" \
  -d '{"algorithm":"both","log_mlflow":true}'
```

Set `MLOPS_RUN_TRAINING=1` to trigger full retrain via subprocess.

### 4. Promote a model to production

```bash
curl -X POST http://localhost:8000/api/mlops/models/promote \
  -H "Content-Type: application/json" \
  -d '{"version":"v3","notes":"Best F1 on holdout"}'
```

This updates `ml-models/best_model.json` and reloads the predictor used by `POST /predict`.

### 5. Docker + MLflow server

```bash
docker compose -f docker-compose.mlops.yml up mlflow
# MLflow UI: http://localhost:5000

docker compose -f docker-compose.mlops.yml up api
# API: http://localhost:8000 (ml-models volume mounted)
```

## API reference

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/mlops/status` | Pipeline health summary |
| GET | `/api/mlops/models` | All registered model versions |
| GET | `/api/mlops/experiments` | Experiment runs |
| GET | `/api/mlops/experiments/compare?versions=v2,v3` | Side-by-side metrics |
| POST | `/api/mlops/experiments/run` | Log or run training experiment |
| POST | `/api/mlops/models/promote` | Deploy version to production |
| GET | `/api/mlops/deployments` | Deployment history |
| GET | `/api/mlops/docker` | Docker build/run commands |

## File layout

```
backend/app/mlops/
  registry.py      # Model version registry
  tracker.py       # MLflow + JSON experiment tracking
  deployment.py    # Promote + hot-reload
  service.py       # Orchestration

ml-models/mlops/
  registry.json
  experiments.json
  deployments.json

datasets/scripts/mlops_experiment.py   # MLflow-enabled training wrapper
docker-compose.mlops.yml               # MLflow + API stack
```

## Recruiter talking points

1. **Versioned artifacts** — v2 (Random Forest) and v3 (XGBoost tuned) with manifests and git commit pins.
2. **Experiment tracking** — MLflow metrics/params with JSON fallback for offline dev.
3. **Promotion workflow** — staging → production via API, not manual file edits.
4. **Containerized deployment** — Docker Compose mounts `ml-models` for reproducible inference.

## Next steps

- Wire CI to run `mlops_experiment.py` on dataset changes
- Add model drift monitoring on `/api/predict` traffic
- Store artifacts in S3 via MLflow artifact store
