from typing import Dict, Any
from fastapi import APIRouter
from app.ml.evaluation import get_latest_model_metrics

router = APIRouter(tags=["ML Model & Evaluation"])


@router.get("/model/evaluation")
def get_model_evaluation() -> Dict[str, Any]:
    metrics = get_latest_model_metrics()
    return metrics
