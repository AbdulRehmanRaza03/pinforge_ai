"""
main.py — PinForge AI FastAPI backend.
Run: uvicorn main:app --reload --port 8000
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import settings
from database import init_db
from routers import accounts, pins, analytics, settings_router
from services import scheduler_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    missing = settings.missing()
    if missing:
        print(f"[WARNING] Missing env vars: {', '.join(missing)}")
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.PROCESSED_DIR, exist_ok=True)
    init_db()
    scheduler_service.start()
    print(f"[PinForge AI] Backend running — ENV={settings.ENV}")
    yield
    # Shutdown
    scheduler_service.stop()


app = FastAPI(
    title="PinForge AI API",
    description="Safe, official Pinterest API v5 automation backend.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (processed images served from backend)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Routers
app.include_router(accounts.router)
app.include_router(pins.router)
app.include_router(analytics.router)
app.include_router(settings_router.router)


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME}
