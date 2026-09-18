from fastapi import FastAPI

from backend.app.api.routes import evidence
from backend.app.api.routes import health
from backend.app.api.routes import memories
from backend.app.api.routes import query


app = FastAPI(
    title="Adaptive AI Memory OS",
    description="Backend API for the Adaptive AI Memory OS",
    version="0.1.0"
)


app.include_router(health.router)
app.include_router(memories.router)
app.include_router(query.router)
app.include_router(evidence.router)
@app.get("/")
def home():
    return {
        "message": "Adaptive AI Memory OS backend is running"
    }