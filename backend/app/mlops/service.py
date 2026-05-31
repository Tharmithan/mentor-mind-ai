"""MLOps orchestration service (Week 7 · Day 5)."""

from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from app.mlops.deployment import DeploymentPipeline
from app.mlops.registry import BEST_MODEL_JSON, ML_MODELS, TRAINING_METRICS, ModelRegistry
from app.mlops.tracker import ExperimentTracker
from app.models.mlops import (
    ExperimentComparison,
    ExperimentRun,
    MLOpsStatus,
    ModelVersion,
    RunExperimentRequest,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
TRAIN_SCRIPT = REPO_ROOT / "datasets" / "scripts" / "mlops_experiment.py"


class MLOpsService:
    def __init__(self) -> None:
        self.registry = ModelRegistry()
        self.tracker = ExperimentTracker()

    def status(self) -> MLOpsStatus:
        versions = self.registry.list_all()
        experiments = self.tracker.sync_from_logs()
        prod = None
        metrics = {}
        if BEST_MODEL_JSON.exists():
            best = json.loads(BEST_MODEL_JSON.read_text(encoding="utf-8"))
            prod = best.get("version")
        if TRAINING_METRICS.exists():
            metrics = json.loads(TRAINING_METRICS.read_text(encoding="utf-8"))

        last_training = None
        if experiments:
            last_training = max(e.started_at for e in experiments)

        dockerfile = REPO_ROOT / "backend" / "Dockerfile"
        return MLOpsStatus(
            production_version=prod,
            total_versions=len(versions),
            total_experiments=len(experiments),
            mlflow_enabled=self.tracker.mlflow_enabled,
            mlflow_uri=self.tracker._mlflow_uri if self.tracker.mlflow_enabled else None,
            docker_ready=dockerfile.exists(),
            git_tracked=(REPO_ROOT / ".git").exists(),
            last_training=last_training,
            current_metrics=metrics,
        )

    def list_models(self) -> list[ModelVersion]:
        return self.registry.list_all()

    def list_experiments(self) -> list[ExperimentRun]:
        return self.tracker.sync_from_logs()

    def compare_experiments(self, versions: list[str] | None = None) -> ExperimentComparison:
        return self.tracker.compare(versions)

    def run_experiment(self, req: RunExperimentRequest) -> dict:
        """Run training script or log a quick experiment record."""
        if TRAIN_SCRIPT.exists() and os.getenv("MLOPS_RUN_TRAINING", "0") == "1":
            return self._run_training_subprocess(req)

        version = req.version_suffix or f"exp_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        metrics_path = TRAINING_METRICS
        metrics = {}
        if metrics_path.exists():
            raw = json.loads(metrics_path.read_text(encoding="utf-8"))
            algo = req.algorithm
            if algo == "both":
                algo = "random_forest"
            block = raw.get(algo, raw.get("random_forest", {}))
            metrics = {
                "r2": block.get("regression", {}).get("r2"),
                "f1": block.get("classification", {}).get("f1"),
                "accuracy": block.get("classification", {}).get("accuracy"),
            }

        run = self.tracker.log_run(
            version=version,
            algorithm=req.algorithm,
            metrics=metrics,
            params={"mode": "record_from_existing_metrics", "algorithm": req.algorithm},
            use_mlflow=req.log_mlflow,
        )
        self.registry.sync_from_disk()
        return {"status": "logged", "experiment": run.model_dump(), "note": "Set MLOPS_RUN_TRAINING=1 for full retrain"}

    def _run_training_subprocess(self, req: RunExperimentRequest) -> dict:
        cmd = [
            "python",
            str(TRAIN_SCRIPT),
            "--algorithm",
            req.algorithm,
        ]
        if req.version_suffix:
            cmd.extend(["--version", req.version_suffix])
        if req.log_mlflow:
            cmd.append("--mlflow")
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT, timeout=600)
        return {
            "status": "completed" if proc.returncode == 0 else "failed",
            "returncode": proc.returncode,
            "stdout": proc.stdout[-2000:] if proc.stdout else "",
            "stderr": proc.stderr[-2000:] if proc.stderr else "",
        }

    def promote(self, version: str, notes: str = "") -> dict:
        record, model = DeploymentPipeline.deploy(version, notes)
        return {"deployment": record.model_dump(), "model": model.model_dump()}

    def deployment_history(self) -> list:
        return [d.model_dump() for d in DeploymentPipeline.list_deployments()]

    def docker_info(self) -> dict:
        return DeploymentPipeline.docker_instructions()
