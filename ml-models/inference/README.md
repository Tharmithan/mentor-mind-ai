# Inference

Production inference runs in:

- `backend/app/ml/predictor.py` — loads `saved_models/` via `model_manifest.json`
- `POST /api/predict` — FastAPI route

No separate inference server required for MVP.
