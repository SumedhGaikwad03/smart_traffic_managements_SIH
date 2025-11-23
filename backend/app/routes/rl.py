# app/routes/rl.py

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any

from app.services.RL_services import apply_manual_signal

router = APIRouter()


class PredictRequest(BaseModel):
    intersections: List[Dict[str, Any]]


@router.post("/api/predict")
async def predict_signals(req: PredictRequest):
    actions = rl_service.predict(req.intersections)
    return {"action": actions}
