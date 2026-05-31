"""Model deployment pipeline (Week 7 · Day 5)."""

from __future__ import annotations

import json
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.models.mlops import DeploymentRecord, ModelVersion
from app.mlops.registry import BEST_MODEL_JSON, ML_MODELS, SAVED_MODELS, ModelRegistry

DEPLOYMENTS_JSON = ML_MODELS / "mlops" / "deployments.json"


class DeploymentPipeline:
    @staticmethod
    def deploy(version: str, notes: str = "") -> tuple[DeploymentRecord, ModelVersion]:
        registry = ModelRegistry()
        model = registry.get(version)
        if model is None:
            raise ValueError(f"Model version {version} not found in registry")

        perf_src = SAVED_MODELS / model.performance_model
        pass_src = SAVED_MODELS / model.pass_fail_model
        if not perf_src.exists():
            perf_src = ML_MODELS / model.performance_model
        if not pass_src.exists():
            pass_src = ML_MODELS / model.pass_fail_model
        if not perf_src.exists():
            raise FileNotFoundError(f"Performance model artifact missing: {model.performance_model}")

        # Copy to production paths consumed by MLPredictor
        prod_score = ML_MODELS / f"saved_models/{model.performance_model}"
        prod_pass = ML_MODELS / f"saved_models/{model.pass_fail_model}"
        prod_score.parent.mkdir(parents=True, exist_ok=True)
        if perf_src.resolve() != prod_score.resolve():
            shutil.copy2(perf_src, prod_score)
        if pass_src.exists() and pass_src.resolve() != prod_pass.resolve():
            shutil.copy2(pass_src, prod_pass)

        best = {
            "score_model": model.algorithm.split("_")[0] if "_" in model.algorithm else model.algorithm,
            "score_file": f"saved_models/{model.performance_model}",
            "pass_model": model.algorithm.split("_")[0] if "_" in model.algorithm else model.algorithm,
            "pass_file": f"saved_models/{model.pass_fail_model}",
            "version": version,
        }
        BEST_MODEL_JSON.write_text(json.dumps(best, indent=2), encoding="utf-8")

        promoted = registry.promote(version)

        record = DeploymentRecord(
            deployment_id=uuid.uuid4().hex[:10],
            version=version,
            status="deployed",
            deployed_at=datetime.now(timezone.utc).isoformat(),
            notes=notes or f"Promoted {version} to production",
        )
        DeploymentPipeline._append_deployment(record)
        DeploymentPipeline._reload_predictor()
        return record, promoted

    @staticmethod
    def _append_deployment(record: DeploymentRecord) -> None:
        DEPLOYMENTS_JSON.parent.mkdir(parents=True, exist_ok=True)
        history = []
        if DEPLOYMENTS_JSON.exists():
            history = json.loads(DEPLOYMENTS_JSON.read_text(encoding="utf-8"))
        history.append(record.model_dump())
        history = history[-20:]
        DEPLOYMENTS_JSON.write_text(json.dumps(history, indent=2), encoding="utf-8")

    @staticmethod
    def list_deployments() -> list[DeploymentRecord]:
        if not DEPLOYMENTS_JSON.exists():
            return []
        data = json.loads(DEPLOYMENTS_JSON.read_text(encoding="utf-8"))
        return [DeploymentRecord(**d) for d in data]

    @staticmethod
    def _reload_predictor() -> None:
        try:
            from app.ai.predictor import get_predictor

            predictor = get_predictor()
            predictor._load()
        except Exception:
            pass

    @staticmethod
    def docker_instructions() -> dict:
        return {
            "build": "docker build -t mentormind-api -f backend/Dockerfile backend/",
            "run": "docker run -p 8000:8000 -v $(pwd)/ml-models:/app/ml-models mentormind-api",
            "mlflow": "docker compose -f docker-compose.mlops.yml up mlflow",
            "note": "Mount ml-models volume so production artifacts are available in container.",
        }
