"""Model version registry (Week 7 · Day 5)."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from app.models.mlops import ModelVersion

REPO_ROOT = Path(__file__).resolve().parents[3]
ML_MODELS = REPO_ROOT / "ml-models"
SAVED_MODELS = ML_MODELS / "saved_models"
REGISTRY_JSON = ML_MODELS / "mlops" / "registry.json"
BEST_MODEL_JSON = ML_MODELS / "best_model.json"
TRAINING_METRICS = ML_MODELS / "training_metrics.json"


class ModelRegistry:
    def __init__(self) -> None:
        self._path = REGISTRY_JSON
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> list[dict]:
        if self._path.exists():
            return json.loads(self._path.read_text(encoding="utf-8"))
        return []

    def _save(self, entries: list[dict]) -> None:
        self._path.write_text(json.dumps(entries, indent=2), encoding="utf-8")

    def sync_from_disk(self) -> list[ModelVersion]:
        """Scan saved_models manifests and training metrics."""
        entries = self._load()
        known = {e["version"] for e in entries}

        metrics = {}
        if TRAINING_METRICS.exists():
            metrics = json.loads(TRAINING_METRICS.read_text(encoding="utf-8"))

        prod_version = None
        if BEST_MODEL_JSON.exists():
            best = json.loads(BEST_MODEL_JSON.read_text(encoding="utf-8"))
            prod_version = best.get("version")

        for manifest_path in sorted(SAVED_MODELS.glob("model_manifest*.json")):
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            ver = data.get("version", "unknown")
            if ver in known:
                continue
            algo = data.get("algorithm") or data.get("score_algorithm", "unknown")
            status = "production" if ver == prod_version else "registered"
            entries.append(
                ModelVersion(
                    version=ver,
                    performance_model=data.get("performance_model", ""),
                    pass_fail_model=data.get("pass_fail_model", ""),
                    algorithm=algo,
                    status=status,
                    metrics=_metrics_for_version(metrics, algo),
                    trained_at=data.get("trained_at", datetime.now(timezone.utc).isoformat()),
                    git_commit=_git_commit(),
                ).model_dump()
            )
            known.add(ver)

        # Seed v2/v3 from joblib if no manifest scan hit
        for ver in ("v2", "v3"):
            if ver in known:
                continue
            perf = SAVED_MODELS / f"performance_model_{ver}.joblib"
            if perf.exists():
                entries.append(
                    ModelVersion(
                        version=ver,
                        performance_model=f"performance_model_{ver}.joblib",
                        pass_fail_model=f"pass_fail_model_{ver}.joblib",
                        algorithm="xgboost" if ver == "v3" else "random_forest",
                        status="production" if ver == prod_version else "registered",
                        metrics=_metrics_for_version(metrics, ver),
                        trained_at=datetime.now(timezone.utc).isoformat(),
                        git_commit=_git_commit(),
                    ).model_dump()
                )

        self._save(entries)
        return self._apply_production_status(entries)

    def _apply_production_status(self, entries: list[dict]) -> list[ModelVersion]:
        prod_version = None
        if BEST_MODEL_JSON.exists():
            best = json.loads(BEST_MODEL_JSON.read_text(encoding="utf-8"))
            prod_version = best.get("version")
        for e in entries:
            if prod_version and e["version"] == prod_version:
                e["status"] = "production"
            elif e.get("status") == "production":
                e["status"] = "archived"
        self._save(entries)
        return [ModelVersion(**e) for e in entries]

    def get(self, version: str) -> ModelVersion | None:
        for m in self.sync_from_disk():
            if m.version == version:
                return m
        return None

    def list_all(self) -> list[ModelVersion]:
        entries = self._load()
        if entries:
            return self._apply_production_status(entries)
        return self.sync_from_disk()

    def promote(self, version: str) -> ModelVersion:
        entries = self._load()
        target = None
        for e in entries:
            if e["version"] == version:
                e["status"] = "production"
                target = e
            elif e["status"] == "production":
                e["status"] = "archived"
        if target is None:
            m = self.get(version)
            if m is None:
                raise ValueError(f"Version {version} not found")
            target = m.model_dump()
            target["status"] = "production"
            entries.append(target)
        self._save(entries)
        return ModelVersion(**target)


def _metrics_for_version(metrics: dict, algo_key: str) -> dict:
    if not metrics:
        return {}
    rf = metrics.get("random_forest", {})
    xgb = metrics.get("xgboost", {})
    if "v3" in str(algo_key) or algo_key == "xgboost":
        return {
            "r2": xgb.get("regression", {}).get("r2"),
            "f1": xgb.get("classification", {}).get("f1"),
            "accuracy": xgb.get("classification", {}).get("accuracy"),
        }
    return {
        "r2": rf.get("regression", {}).get("r2"),
        "f1": rf.get("classification", {}).get("f1"),
        "accuracy": rf.get("classification", {}).get("accuracy"),
    }


def _git_commit() -> str | None:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=5,
        )
        if out.returncode == 0:
            return out.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return None
