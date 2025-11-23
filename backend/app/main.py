"""
main.py
FastAPI app bootstrap for Smart Traffic Management Backend.

- Registers routers for state, control, metrics, dashboard.
- Loads simple CORS policy using FRONTEND_ORIGIN from config.
- Provides a lightweight health endpoint.
- Prints useful startup logs.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Routers
from app.routes import state, control, metrics, dashboard, settings
from app.routes import rl  # <-- ADD THIS IMPORT

# Small config loader
from app.utils.config import FRONTEND_ORIGIN, APP_HOST, APP_PORT, DEBUG, LOG_LEVEL

# Configure logging early
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger("smart-traffic-backend")

app = FastAPI(
    title="Smart Traffic Management Backend",
    description="Backend API for simulation, traffic analytics, and AI-driven optimization.",
    version="1.0.0",
    debug=DEBUG,
)

# -----------------------
# Register Routers
# -----------------------
app.include_router(state.router, prefix="/api")
app.include_router(control.router, prefix="/api")
app.include_router(metrics.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(settings.router, prefix="/api")

# ADD THIS FOR AI PREDICTION ENDPOINT
app.include_router(rl.router, prefix="/api")   # <-- REQUIRED


# -----------------------
# CORS
# -----------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN] if FRONTEND_ORIGIN else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------
# Health endpoints
# -----------------------
@app.get("/")
def root():
    return {"message": "🚦 Smart Traffic Management Backend is running!"}

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "smart-traffic-backend",
        "host": APP_HOST,
        "port": APP_PORT
    }

# -----------------------
# Startup logs
# -----------------------
@app.on_event("startup")
def on_startup():
    logger.info("Starting Smart Traffic Management Backend")
    logger.info("Frontend origin allowed: %s", FRONTEND_ORIGIN)
    logger.info("Debug mode: %s", DEBUG)
    from app.utils.config import SUMO_ENABLED, SUMO_CONFIG, SIMULATION_MOCK
    logger.info(f"SUMO_ENABLED = {SUMO_ENABLED}")
    logger.info(f"SIMULATION_MOCK = {SIMULATION_MOCK}")
    logger.info(f"SUMO_CONFIG = {SUMO_CONFIG}")
    from app.utils.config import getenv
    print("TEST_ENV ->", getenv("TEST_ENV"))



@app.on_event("shutdown")
def on_shutdown():
    logger.info("Shutting down Smart Traffic Management Backend")
    logger.info("Goodbye! 👋")