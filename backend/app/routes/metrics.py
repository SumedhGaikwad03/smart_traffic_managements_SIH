# Endpoint: KPIs (wait times, throughput, etc.)
from fastapi import APIRouter
from app.models.traffic import Metrics

router = APIRouter(tags=["Metrics"])

@router.get("/metrics", response_model=Metrics)
def get_metrics():
    # Mock KPI values
    return {
        "avg_commute_time": 15.3,
        "throughput": 240,
        "congestion_index": 0.72
    }
