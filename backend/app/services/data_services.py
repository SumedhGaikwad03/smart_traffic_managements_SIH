import random
from typing import List, Dict

def mock_intersection(idx: int) -> Dict:
    return {
        "id": f"I{idx}",
        "queues": {
            "N": random.randint(0, 15),
            "S": random.randint(0, 15),
            "E": random.randint(0, 15),
            "W": random.randint(0, 15),
        },
        "processed": random.randint(40, 200),
        "avg_wait": round(random.uniform(5, 40), 2),
        "signals": {
            "NORTH": random.choice(["GREEN", "YELLOW", "RED"]),
            "SOUTH": random.choice(["GREEN", "YELLOW", "RED"]),
            "EAST": random.choice(["GREEN", "YELLOW", "RED"]),
            "WEST": random.choice(["GREEN", "YELLOW", "RED"]),
        },
        "position": [random.uniform(0, 500), random.uniform(0, 500)],
    }

def generate_mock_state(n=4) -> List[Dict]:
    return [mock_intersection(i) for i in range(n)]
