from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from backend.app.api.routes import evidence
from backend.app.api.routes import health
from backend.app.api.routes import memories
from backend.app.api.routes import permissions
from backend.app.api.routes import query


app = FastAPI(
    title="Adaptive AI Memory OS",
    description="Backend API for the Adaptive AI Memory OS",
    version="0.1.0",
)


app.include_router(health.router)
app.include_router(memories.router)
app.include_router(query.router)
app.include_router(evidence.router)
app.include_router(permissions.router)


@app.exception_handler(Exception)
async def unexpected_exception_handler(
    request: Request,
    exc: Exception,
):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error.",
        },
    )


@app.get("/")
def home():
    return {
        "message": "Adaptive AI Memory OS backend is running"
    }