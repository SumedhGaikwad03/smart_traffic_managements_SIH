# app/routes/control.py

from fastapi import APIRouter
from time import time
from app.models.traffic import ControlAction

# Manual mock signals
from app.services.RL_services import apply_manual_signal

router = APIRouter(tags=["Control"])

last_applied_action: dict | None = None


@router.post("/control", response_model=ControlAction)
def control_signal(action: ControlAction):
    global last_applied_action

    apply_manual_signal(action.intersection, action.action)

    last_applied_action = {
        "timestamp": time(),
        "intersection": action.intersection,
        "action": action.action,
    }

    return action


@router.get("/control/last")
def get_last_action():
    return last_applied_action or {"message": "No control applied yet."}
