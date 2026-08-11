"""FastAPI entry point"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os

from app.core.database import engine
from app.api import planning, settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(
    title="TourismAI",
    description="AI-powered trip planning with Amap + LLM Agent",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(planning.router, tags=["Trip Planning"])
app.include_router(settings.router, tags=["Settings"])

DEMO_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "demo")


@app.get("/demo")
async def demo_page():
    demo_file = os.path.join(DEMO_DIR, "index.html")
    if os.path.exists(demo_file):
        return FileResponse(demo_file)
    return {"message": "demo/index.html not found"}


@app.get("/")
async def root():
    return {
        "service": "TourismAI",
        "docs": "/docs",
        "demo": "/demo",
        "api": {
            "Plan": "POST /api/plan",
            "Stream": "POST /api/plan/stream",
            "History": "GET /api/plans",
            "Settings": "GET|PUT /api/settings",
        },
    }