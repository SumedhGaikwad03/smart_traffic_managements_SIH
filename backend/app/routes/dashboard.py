 # Endpoint: stream live data for frontend
from fastapi import APIRouter

router = APIRouter(tags=["Dashboard"])

@router.get("/dashboard")
def dashboard_data():
    # Mock summary response
    return {
        "status": "live",
        "intersections": 4,
        "emergency_vehicles": 1
    }
