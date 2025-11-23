import os
import traci
from time import time
from app.models.traffic import (
    TrafficState, IntersectionData, VehicleState, EdgeShape
)
from app.utils.config import SUMO_BINARY, SUMO_CONFIG, SUMO_ENABLED
import math

_running = False


def start_sumo():
    global _running
    print("[SUMO] CONFIG =", SUMO_CONFIG)
    print("[DEBUG] Loading SUMO CONFIG:", SUMO_CONFIG)
    print("[DEBUG] Exists:", os.path.exists(SUMO_CONFIG))

    if not SUMO_ENABLED:
        return

    # If connection already alive, do nothing
    try:
        if traci.isLoaded():    # <--- This is the important part
            return
    except:
        pass

    if _running:
        return

    try:
        traci.start([SUMO_BINARY, "-c", SUMO_CONFIG])
        _running = True
        print("[SUMO] NET FILE =", traci.simulation.getNetFilename())

        print("[SUMO] Connected successfully")
    except Exception as e:
        print("SUMO already running or failed:", e)
    
    print("[TLS IDS]", traci.trafficlight.getIDList())
    


def step_simulation():
    if SUMO_ENABLED:
        start_sumo()
        traci.simulationStep()


# Better lane→direction mapping
def infer_direction(lane: str) -> str:
    lane = lane.lower()

    # Tune these patterns to your actual lane IDs
    if "n2" in lane or "2n" in lane or "north" in lane:
        return "NORTH"
    if "s2" in lane or "2s" in lane or "south" in lane:
        return "SOUTH"
    if "e2" in lane or "2e" in lane or "east" in lane:
        return "EAST"
    if "w2" in lane or "2w" in lane or "west" in lane:
        return "WEST"

    return "UNKNOWN"




def get_edges():
    edges_out = []

    edge_ids = traci.edge.getIDList()
    lane_ids = traci.lane.getIDList()

    print("EDGES =", edge_ids)
    print("LANES =", lane_ids)

    for edge_id in edge_ids:

        # Skip internal edges like ":center_0"
        if edge_id.startswith(":"):
            continue

        shape = []

        # SUMO lanes are named like "edgeID_0"
        lane_id = f"{edge_id}_0"

        if lane_id in lane_ids:
            try:
                shape = traci.lane.getShape(lane_id)
            except Exception as e:
                print(f"[WARN] Failed getting shape for lane {lane_id}: {e}")
                shape = []

        edges_out.append({
            "id": edge_id,
            "shape": shape
        })
    print("[EDGE OUTPUT]", edges_out)
    return edges_out




def get_vehicles():
    vehicles = []
    for vid in traci.vehicle.getIDList():
        x, y = traci.vehicle.getPosition(vid)
        speed = traci.vehicle.getSpeed(vid)
        lane = traci.vehicle.getLaneID(vid)
        wait = traci.vehicle.getWaitingTime(vid)

        angle = traci.vehicle.getAngle(vid)
        vx = math.cos(math.radians(angle))
        vy = math.sin(math.radians(angle))

        vehicles.append(VehicleState(
            id=vid,
            x=x, y=y,
            speed=speed,
            lane=lane,
            waiting_time=wait,
            vx=vx, vy=vy
        ))
    return vehicles


def get_signal_map(tls_id):
    state = traci.trafficlight.getRedYellowGreenState(tls_id)
    lanes = traci.trafficlight.getControlledLanes(tls_id)

    direction_states = {
        "NORTH": [],
        "SOUTH": [],
        "EAST": [],
        "WEST": []
    }

    for i, lane in enumerate(lanes):
        d = infer_direction(lane)
        color = state[i]

        # Skip lanes we can't classify
        if d not in direction_states:
            # optional debug:
            # print(f"[WARN] Unknown direction for lane {lane} (tls={tls_id})")
            continue

        if color == "G":
            direction_states[d].append("GREEN")
        elif color.lower() == "y":
            direction_states[d].append("YELLOW")
        else:
            direction_states[d].append("RED")

    mapping = {}
    for d, colors in direction_states.items():
        if not colors:
            mapping[d] = "RED"
        elif colors.count("GREEN") >= 2:
            mapping[d] = "GREEN"
        elif colors.count("YELLOW") >= 2:
            mapping[d] = "YELLOW"
        else:
            mapping[d] = "RED"

    return mapping







def get_traffic_states() -> TrafficState:
    step_simulation()

    intersections_out = []

    for tls_id in traci.trafficlight.getIDList():
        lanes = traci.trafficlight.getControlledLanes(tls_id)
        phase_index = traci.trafficlight.getPhase(tls_id)

        queue_counts = {}
        waits = []

        for lane in lanes:
            direction = infer_direction(lane)

            if direction == "UNKNOWN":
                continue  # skip weird lanes / internals

            vehs = traci.lane.getLastStepVehicleIDs(lane)

            queue_counts.setdefault(direction, 0)
            queue_counts[direction] += len(vehs)

            for v in vehs:
                waits.append(traci.vehicle.getWaitingTime(v))

        avg_wait = (sum(waits) / len(waits)) if waits else 0

        try:
            x, y = traci.junction.getPosition(tls_id)
        except:
            x, y = (0, 0)

        intersections_out.append(IntersectionData(
            id=tls_id,
            queues=queue_counts,
            processed=0,
            avg_wait=avg_wait,
            signals=get_signal_map(tls_id),
            phase=phase_index,
            position=[x, y]
        ))

    return TrafficState(
        timestamp=time(),
        intersections=intersections_out,
        vehicles=get_vehicles(),
        edges=get_edges()
    )
