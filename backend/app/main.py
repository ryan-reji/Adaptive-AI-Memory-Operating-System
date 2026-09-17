from fastapi import FastAPI

from backend.app.api.routes import health
from backend.app.api.routes import memories


app = FastAPI(
    title="Adaptive AI Memory OS",
    description="Backend API for the Adaptive AI Memory OS",
    version="0.1.0"
)


app.include_router(health.router)
app.include_router(memories.router)


@app.get("/")
def home():
    return {
        "message": "Adaptive AI Memory OS backend is running"
    }