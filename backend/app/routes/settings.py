# app/routes/settings.py
from fastapi import APIRouter, HTTPException
from app.models.traffic import SettingsUpdate
from time import time

router = APIRouter(tags=["Settings"])

# In-memory settings store (replace with DB or config later)
_CURRENT_SETTINGS = {
    "optimization_strategy": "manual",  # "manual" or "ai"
    "last_updated": time()
}

@router.post("/settings")
def update_settings(settings: SettingsUpdate):
    """
    Update optimization mode. Frontend uses this to switch between
    AI-controlled optimization and manual control.
    """
    opt = settings.optimization_strategy.lower()
    if opt not in ("ai", "manual", "adaptive", "rl", "rule_based"):
        # accept a few synonyms but prefer ai/manual on the frontend
        raise HTTPException(status_code=400, detail="Unsupported optimization_strategy")
    # normalize to simple values used by the frontend
    if opt in ("ai", "rl", "adaptive"):
        _CURRENT_SETTINGS["optimization_strategy"] = "ai"
    else:
        _CURRENT_SETTINGS["optimization_strategy"] = "manual"

    _CURRENT_SETTINGS["last_updated"] = time()
    return {"status": "ok", "current": _CURRENT_SETTINGS}

@router.get("/settings")
def get_settings():
    """
    Return current settings (used by frontend to know if AI is active).
    """
    return _CURRENT_SETTINGS
