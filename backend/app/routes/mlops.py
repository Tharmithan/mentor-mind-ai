"""MLOps API routes (Week 7 · Day 5)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.mlops.service import MLOpsService
from app.models.mlops import PromoteRequest, RunExperimentRequest

router = APIRouter(prefix="/mlops", tags=["mlops"])
_service: MLOpsService | None = None


def get_mlops_service() -> MLOpsService:
    global _service
    if _service is None:
        _service = MLOpsService()
    return _service


@router.get("/status")
def mlops_status():
    return get_mlops_service().status()


@router.get("/models")
def list_models():
    return get_mlops_service().list_models()


@router.get("/experiments")
def list_experiments():
    return get_mlops_service().list_experiments()


@router.get("/experiments/compare")
def compare_experiments(versions: str | None = Query(None, description="Comma-separated versions e.g. v2,v3")):
    ver_list = [v.strip() for v in versions.split(",")] if versions else None
    return get_mlops_service().compare_experiments(ver_list)


@router.post("/experiments/run")
def run_experiment(body: RunExperimentRequest):
    return get_mlops_service().run_experiment(body)


@router.post("/models/promote")
def promote_model(body: PromoteRequest):
    try:
        return get_mlops_service().promote(body.version, body.notes)
    except (ValueError, FileNotFoundError) as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get("/deployments")
def deployment_history():
    return get_mlops_service().deployment_history()


@router.get("/docker")
def docker_info():
    return get_mlops_service().docker_info()
