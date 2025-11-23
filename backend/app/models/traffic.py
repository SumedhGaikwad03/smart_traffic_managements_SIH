"""
traffic.py  
Unified Pydantic models for:
- SUMO state
- Frontend grid
- RL agent input/output
- Metrics panel
"""

from typing import Dict, List, Optional
from pydantic import BaseModel


# -------------------------------------------------------------
# VEHICLE MODEL
# -------------------------------------------------------------

class VehicleData(BaseModel):
    id: str
    x: float
    y: float
    speed: float
    lane: Optional[str] = None
    waiting_time: Optional[float] = None


# -------------------------------------------------------------
# INTERSECTION MODEL
# -------------------------------------------------------------

class IntersectionData(BaseModel):
    id: str                                      # e.g. "A1", SUMO tls id
    queues: Dict[str, int]                       # {"N": 3, "S": 5 ...}

    processed: int                               # total vehicles passed
    avg_wait: float   
    phase: int                           # current traffic light phase

    signals: Dict[str, str]                      # {"NORTH": "GREEN", ...}

    position: List[float]                        # [x, y] world coords


# -------------------------------------------------------------
# SYSTEM-WIDE TRAFFIC STATE
# -------------------------------------------------------------

class EdgeShape(BaseModel):
    id: str
    shape: List[List[float]]

class VehicleState(BaseModel):
    id: str
    x: float
    y: float
    speed: float
    lane: str
    waiting_time: float
    vx: float = 0
    vy: float = 0

class TrafficState(BaseModel):
    timestamp: float
    intersections: List[IntersectionData]
    vehicles: List[VehicleState]
    edges: List[EdgeShape]


# -------------------------------------------------------------
# CONTROL ACTIONS
# -------------------------------------------------------------

class ControlAction(BaseModel):
    intersection: str
    action: str                                  # e.g., "GREEN_NORTH"


# -------------------------------------------------------------
# METRICS DATA FOR DASHBOARD
# -------------------------------------------------------------

class MetricsData(BaseModel):
    avg_wait_time: float
    total_processed: int
    throughput: int
    congestion_index: float
    optimization_strategy: str

    wait_time_history: Optional[List[float]] = None
    throughput_history: Optional[List[int]] = None


# -------------------------------------------------------------
# SETTINGS UPDATE MODEL
# -------------------------------------------------------------

class SettingsUpdate(BaseModel):
    optimization_strategy: str                   # "ai", "manual", etc.


# -------------------------------------------------------------
# EXPORT MODEL
# -------------------------------------------------------------

class ExportedData(BaseModel):
    timestamp: float
    metrics: MetricsData
    intersections: List[IntersectionData]
    vehicles: List[VehicleData] = []
