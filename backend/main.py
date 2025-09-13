from fastapi import FastAPI
from app.routes import state, control, metrics, dashboard

app = FastAPI(title="Smart Traffic Management Backend")

# Register routers
app.include_router(state.router, prefix="/api")
app.include_router(control.router, prefix="/api")
app.include_router(metrics.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "🚦 Smart Traffic Management Backend is running!"}
