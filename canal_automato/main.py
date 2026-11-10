from __future__ import annotations

import logging
from pathlib import Path

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .config import ASSETS_DIR, CHANNEL_NAME, LOGO_PATH, ROOT, ensure_dirs
from .engine import engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

ensure_dirs()
static_dir = ROOT / "static"


@asynccontextmanager
async def lifespan(_: FastAPI):
    engine.start()
    yield
    engine.stop()


app = FastAPI(title=CHANNEL_NAME, lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")


class ProgressBody(BaseModel):
    watched_sec: float = 0
    duration_sec: float | None = None


class EndedBody(BaseModel):
    watched_sec: float = 0
    duration_sec: float | None = None
    completed: bool = True


@app.get("/", response_class=HTMLResponse)
def index() -> FileResponse:
    return FileResponse(static_dir / "index.html")


@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "channel": CHANNEL_NAME}


@app.get("/api/state")
def state() -> dict:
    return engine.snapshot().model_dump()


@app.post("/api/progress")
def progress(body: ProgressBody) -> dict:
    return engine.report_progress(body.watched_sec, body.duration_sec)


@app.post("/api/ended")
def ended(body: EndedBody) -> dict:
    if body.duration_sec is not None:
        engine.report_progress(body.watched_sec or body.duration_sec, body.duration_sec)
    return engine.report_ended()


@app.get("/logo")
def logo() -> FileResponse:
    if LOGO_PATH.exists():
        return FileResponse(LOGO_PATH)
    return FileResponse(static_dir / "index.html")
