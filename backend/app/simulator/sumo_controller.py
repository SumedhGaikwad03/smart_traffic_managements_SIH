# app/simulator/controller.py
import traci
from app.models.traffic import TrafficState, ControlAction, Metrics

SUMO_BINARY = "sumo"   # or "sumo-gui" for visualization
SUMO_CONFIG = "sumo_network/myconfig.sumocfg"
_running = False

def start_sumo():
    global _running
    if not _running:
        traci.start([SUMO_BINARY, "-c", SUMO_CONFIG])
        _running = True

def step_simulation():
    start_sumo()
    traci.simulationStep()

def get_traffic_states():
    step_simulation()
    states = []
    for tls in traci.trafficlight.getIDList():
        lanes = traci.trafficlight.getControlledLanes(tls)
        vehicles = []
        for lane in lanes:
            vehicles.extend(traci.lane.getLastStepVehicleIDs(lane))

        avg_wait_time = 0.0
        if vehicles:
            waits = [traci.vehicle.getWaitingTime(v) for v in vehicles]
            avg_wait_time = sum(waits) / len(waits)

        states.append(
            TrafficState(
                intersection=tls,
                vehicles_waiting=len(vehicles),
                avg_wait_time=avg_wait_time
            )
        )
    return states

def get_control_actions():
    step_simulation()
    actions = []
    for tls in traci.trafficlight.getIDList():
        state = traci.trafficlight.getRedYellowGreenState(tls)
        if "G" in state:
            action = "GREEN"
        elif "y" in state or "Y" in state:
            action = "YELLOW"
        else:
            action = "RED"
        actions.append(ControlAction(intersection=tls, action=action))
    return actions

def get_metrics():
    step_simulation()
    total_vehicles = traci.vehicle.getIDCount()
    waits = [traci.vehicle.getWaitingTime(v) for v in traci.vehicle.getIDList()]
    avg_commute_time = sum(waits) / max(1, len(waits))
    congestion_index = sum(len(traci.lane.getLastStepVehicleIDs(lane)) for lane in traci.lane.getIDList())
    congestion_index /= max(1, len(traci.lane.getIDList()) * 10)

    return Metrics(
        avg_commute_time=avg_commute_time,
        throughput=total_vehicles,
        congestion_index=congestion_index
    )
