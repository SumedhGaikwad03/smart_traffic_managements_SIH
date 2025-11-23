# app/services/RL_service.py

import traci

PHASE_MAP = {
    "NS_GREEN": 0,
    "NS_YELLOW": 1,
    "ALL_RED": 2,
    "EW_GREEN": 3,
    "EW_YELLOW": 4,
}

def apply_manual_signal(tls_id: str, action: str):
    if tls_id not in traci.trafficlight.getIDList():
        raise ValueError(f"Invalid traffic light ID: {tls_id}")

    if action not in PHASE_MAP:
        raise ValueError(f"Invalid action: {action}")

    phase_index = PHASE_MAP[action]

    try:
        traci.trafficlight.setPhase(tls_id, phase_index)

        print(
            f"[MANUAL SIGNAL] {tls_id} → {action} | "
            f"phase={phase_index} | "
            f"actual={traci.trafficlight.getRedYellowGreenState(tls_id)}"
        )

    except Exception as e:
        print(f"[ERROR] Failed to apply signal {action} on {tls_id}: {e}")
        raise



def _apply_simple_tls(tls_id, action):
    # east, south, west have 1-lane TLs
    if action in ("NS_GREEN", "EW_GREEN"):
        traci.trafficlight.setRedYellowGreenState(tls_id, "G")
    else:
        traci.trafficlight.setRedYellowGreenState(tls_id, "r")


def get_signal_for(tls_id: str, direction: str):
    try:
        return traci.trafficlight.getRedYellowGreenState(tls_id)
    except:
        return "UNKNOWN"
