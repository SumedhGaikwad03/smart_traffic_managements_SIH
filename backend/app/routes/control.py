 # Endpoint: apply RL decision (control signals)
from fastapi import APIRouter
from app.models.traffic import ControlAction

router = APIRouter(tags=["Control"])

@router.post("/control", response_model=ControlAction)
def control_signal(action: ControlAction):
    # Mock: just return what admin/RL sends

    return action 
