"""Pydantic models for MLOps Pipeline (Week 7 · Day 5)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ModelVersion(BaseModel):
    version: str
    performance_model: str
    pass_fail_model: str
    algorithm: str
    status: str = "registered"  # registered | staging | production | archived
    metrics: dict = Field(default_factory=dict)
    trained_at: str
    git_commit: str | None = None
    experiment_id: str | None = None


class ExperimentRun(BaseModel):
    experiment_id: str
    run_name: str
    version: str
    algorithm: str
    status: str = "completed"
    metrics: dict = Field(default_factory=dict)
    params: dict = Field(default_factory=dict)
    artifacts: list[str] = Field(default_factory=list)
    started_at: str
    ended_at: str | None = None
    mlflow_run_id: str | None = None


class ExperimentComparison(BaseModel):
    experiments: list[ExperimentRun]
    best_regression: str
    best_classification: str
    recommendation: str


class DeploymentRecord(BaseModel):
    deployment_id: str
    version: str
    status: str
    deployed_at: str
    deployed_by: str = "api"
    notes: str = ""


class MLOpsStatus(BaseModel):
    production_version: str | None
    total_versions: int
    total_experiments: int
    mlflow_enabled: bool
    mlflow_uri: str | None
    docker_ready: bool
    git_tracked: bool
    last_training: str | None
    current_metrics: dict = Field(default_factory=dict)


class PromoteRequest(BaseModel):
    version: str
    notes: str = ""


class RunExperimentRequest(BaseModel):
    algorithm: str = "random_forest"  # random_forest | xgboost | both
    version_suffix: str | None = None
    log_mlflow: bool = True
