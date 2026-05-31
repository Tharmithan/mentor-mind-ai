"""MLflow-enabled training experiment (Week 7 · Day 5).

Wraps existing train_models logic and logs params/metrics/artifacts to MLflow.
Usage:
  python datasets/scripts/mlops_experiment.py --algorithm random_forest --mlflow
  python datasets/scripts/mlops_experiment.py --algorithm xgboost --version v4 --mlflow
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "datasets" / "scripts"))

ML_MODELS = ROOT / "ml-models"
LOGS_DIR = ML_MODELS / "training" / "logs"
MLFLOW_DIR = ML_MODELS / "mlflow"


def main() -> int:
    parser = argparse.ArgumentParser(description="MLOps training experiment")
    parser.add_argument("--algorithm", choices=["random_forest", "xgboost", "both"], default="both")
    parser.add_argument("--version", default=None, help="Version tag e.g. v4")
    parser.add_argument("--mlflow", action="store_true", help="Log to MLflow")
    args = parser.parse_args()

    version = args.version or datetime.now(timezone.utc).strftime("v%Y%m%d")
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    try:
        import train_models as tm
    except ImportError:
        print("train_models.py not found; writing stub log only", file=sys.stderr)
        _write_stub_log(version, args.algorithm)
        return 0

    metrics = {}
    if hasattr(tm, "train_and_evaluate"):
        metrics = tm.train_and_evaluate()
    elif hasattr(tm, "main"):
        tm.main()
        metrics_path = ML_MODELS / "training_metrics.json"
        if metrics_path.exists():
            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))

    log_entry = {
        "version": version,
        "algorithm": args.algorithm,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "metrics": metrics,
        "artifacts": [
            f"saved_models/performance_model_{version}.joblib",
            f"saved_models/pass_fail_model_{version}.joblib",
        ],
    }
    log_path = LOGS_DIR / f"training_log_{version}.json"
    log_path.write_text(json.dumps(log_entry, indent=2), encoding="utf-8")
    print(f"Training log written: {log_path}")

    if args.mlflow:
        _log_mlflow(version, args.algorithm, metrics)

    return 0


def _write_stub_log(version: str, algorithm: str) -> None:
    metrics_path = ML_MODELS / "training_metrics.json"
    metrics = {}
    if metrics_path.exists():
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    log_entry = {
        "version": version,
        "algorithm": algorithm,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "metrics": metrics,
        "artifacts": [],
    }
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    (LOGS_DIR / f"training_log_{version}.json").write_text(json.dumps(log_entry, indent=2))


def _log_mlflow(version: str, algorithm: str, metrics: dict) -> None:
    try:
        import mlflow

        uri = f"file:{MLFLOW_DIR / 'mlruns'}"
        mlflow.set_tracking_uri(uri)
        mlflow.set_experiment("mentormind_student_performance")
        with mlflow.start_run(run_name=f"{algorithm}_{version}"):
            mlflow.log_param("version", version)
            mlflow.log_param("algorithm", algorithm)
            for algo_name, block in metrics.items():
                if not isinstance(block, dict):
                    continue
                for kind, vals in block.items():
                    if isinstance(vals, dict):
                        for k, v in vals.items():
                            if isinstance(v, (int, float)):
                                mlflow.log_metric(f"{algo_name}_{kind}_{k}", float(v))
        print(f"MLflow logged to {uri}")
    except ImportError:
        print("mlflow not installed; skip MLflow logging", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
