"""
state.py
Delivers live traffic state to frontend.
Uses mock state unless SUMO is enabled.
"""

from fastapi import APIRouter
from time import time
from typing import Optional

# Data models
from app.models.traffic import TrafficState, IntersectionData

# Config
from app.utils.config import SIMULATION_MOCK

# Read manual signals
from app.services.RL_services import get_signal_for

router = APIRouter(tags=["Traffic State"])


def mock_get_state() -> TrafficState:
    """
    Returns simulated traffic state for frontend.
    Uses manual signals if user applied them.
    """

    intersections = [
        IntersectionData(
            id="A1",
            queues={"N": 5, "S": 3, "E": 4, "W": 2},
            processed=120,
            avg_wait=22.3,
            signals={
                "NORTH": get_signal_for("A1", "N"),
                "SOUTH": get_signal_for("A1", "S"),
                "EAST":  get_signal_for("A1", "E"),
                "WEST":  get_signal_for("A1", "W"),
            },
            position=[100, 200],
        ),
        IntersectionData(
            id="B2",
            queues={"N": 2, "S": 6, "E": 1, "W": 3},
            processed=98,
            avg_wait=18.7,
            signals={
                "NORTH": get_signal_for("B2", "N"),
                "SOUTH": get_signal_for("B2", "S"),
                "EAST":  get_signal_for("B2", "E"),
                "WEST":  get_signal_for("B2", "W"),
            },
            position=[300, 420],
        ),
    ]

    return TrafficState(timestamp=time(), intersections=intersections)


def _get_state_from_sumo() -> Optional[TrafficState]:
    """
    If SUMO is enabled, fetch real state.
    Only calls SUMO once per request.
    """
    try:
        from app.simulator.sumo_controller import get_traffic_states
        return get_traffic_states()   # No double stepping
    except Exception as e:
        print("SUMO error, fallback to MOCK:", e)
        return None
    

@router.get("/state", response_model=TrafficState)
def get_state():
    if SIMULATION_MOCK:
        return mock_get_state()

    from app.simulator.sumo_controller import get_traffic_states
    return get_traffic_states()
