# utils/config.py
from pathlib import Path
from dotenv import load_dotenv
import os

# Auto-load .env in project root (backend/)
env_path = Path(__file__).resolve().parents[2] / ".env"
print(">>> CONFIG DEBUG")
print("env_path =", env_path)
print("env exists =", env_path.exists())
print("SUMO_ENABLED(raw) =", os.getenv("SUMO_ENABLED"))
print("SIMULATION_MOCK(raw) =", os.getenv("SIMULATION_MOCK"))
print("SUMO_CONFIG(raw) =", os.getenv("SUMO_CONFIG"))
print("------")

if env_path.exists():
    load_dotenv(env_path)

def getenv(key: str, default=None, cast=str):
    val = os.getenv(key, default)
    if val is None:
        return default
    if cast is bool:
        return str(val).lower() in ("1", "true", "yes", "on")
    try:
        return cast(val)
    except Exception:
        return val

# App
APP_HOST = getenv("APP_HOST", "127.0.0.1")
APP_PORT = getenv("APP_PORT", 8000, int)
DEBUG = getenv("DEBUG", "false", bool)

# SUMO
SUMO_ENABLED = getenv("SUMO_ENABLED", "false", bool)
SUMO_BINARY = getenv("SUMO_BINARY", "sumo")
SUMO_CONFIG = str(Path(getenv("SUMO_CONFIG", "sumo_network/myconfig.sumocfg")).resolve())
# Simulation / mocking
SIMULATION_MOCK = getenv("SIMULATION_MOCK", "true", bool)
SIMULATION_STEP_SECONDS = getenv("SIMULATION_STEP_SECONDS", 1, int)

# CORS
FRONTEND_ORIGIN = getenv("FRONTEND_ORIGIN", "http://localhost:3000")

# Logging
LOG_LEVEL = getenv("LOG_LEVEL", "INFO")
