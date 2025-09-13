# app/routes/state.py , this workks but for now we are a just waiting for sumo to be fully integrated
from fastapi import APIRouter
from app.models.traffic import TrafficState
from app.simulator.sumo_controller import step_simulation, get_traffic_states

router = APIRouter(tags=["Traffic State"])

@router.get("/state", response_model=list[TrafficState])
def get_state():
    """
    Fetch current traffic state from SUMO.
    Advances simulation by 1 step and returns TrafficState for all intersections.
    """
    # Advance SUMO simulation by 1 step
    step_simulation()

    # Fetch all intersections' traffic states
    return get_traffic_states()
