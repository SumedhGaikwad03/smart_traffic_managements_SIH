"""
dashboard.py
Provides high-level dashboard summary data:
- System status
- Simulation metadata
- Alerts / notifications
- Global KPIs

This endpoint is meant for the dashboard header + summary cards.
"""

from fastapi import APIRouter
from time import time

router = APIRouter(tags=["Dashboard"])

# -----------------------------------------------------------------------
# Temporary mock data until SUMO + RL pipeline is integrated
# -----------------------------------------------------------------------
SIMULATION_RUNNING = False
LAST_OPTIMIZED = time()

@router.get("/dashboard")
def dashboard_data():
    """
    Returns a summarized view of system status for the dashboard.
    
    Frontend uses this endpoint for:
    - Header status ("System Active" / "Idle")
    - Emergency alerts
    - Count of intersections
    - Metadata about optimization engine
    """

    return {
        "status": "running" if SIMULATION_RUNNING else "idle",
        "timestamp": time(),
        "intersections_total": 4,                # mock
        "active_strategy": "adaptive",           # mock
        "last_optimized": LAST_OPTIMIZED,        # mock
        "alerts": {
            "emergency_vehicles": 1,             # mock
            "high_congestion_nodes": ["A1"],     # mock
        }
    }
