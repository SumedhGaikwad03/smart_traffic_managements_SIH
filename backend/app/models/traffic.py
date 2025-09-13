 # Schema: state, actions, metrics JSON 

# these are all json formats for traffic state, control actions, and KPIs
from pydantic import BaseModel

class TrafficState(BaseModel):
    intersection: str
    vehicles_waiting: int
    avg_wait_time: float

class ControlAction(BaseModel):
    intersection: str
    action: str  # e.g., "GREEN", "RED", "YELLOW"

class Metrics(BaseModel):
    avg_commute_time: float
    throughput: int
    congestion_index: float
