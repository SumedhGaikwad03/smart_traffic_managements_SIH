"""
metrics.py
Provides system-wide KPIs for the dashboard:
- Average wait time
- Throughput
- Congestion index
- Optimization strategy
- KPI history (for charts)
"""

from fastapi import APIRouter
from time import time
from app.models.traffic import MetricsData

router = APIRouter(tags=["Metrics"])

# -------------------------------------------------------------------
# TEMPORARY MOCK METRICS (until SUMO + RL integration is ready)
# This lets the dashboard render graph data and stats properly.
# Replace these values with real simulation metrics later.
# -------------------------------------------------------------------

wait_history = [28.0, 26.5, 22.1, 20.3, 19.7]
throughput_history = [180, 190, 205, 220, 240]

@router.get("/metrics", response_model=MetricsData)
def get_metrics():
    """
    Returns global system KPIs used by the frontend dashboard.
    Later, this will collect metrics from SUMO simulation
    + RL engine.
    """

    # Mock values
    avg_wait = sum(wait_history) / len(wait_history)
    throughput = throughput_history[-1]
    congestion = avg_wait / 60  # normalized mock value

    return MetricsData(
        avg_wait_time=avg_wait,
        total_processed=1300,          # mock
        throughput=throughput,
        congestion_index=round(congestion, 2),
        optimization_strategy="adaptive",
        wait_time_history=wait_history,
        throughput_history=throughput_history
    )
