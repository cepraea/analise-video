from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from cepraea_video import __version__
from cepraea_video.config import ensure_runtime_directories


@asynccontextmanager
async def lifespan(_: FastAPI):
    ensure_runtime_directories()
    yield


app = FastAPI(
    title="CEPRAEA Video Analysis",
    version=__version__,
    lifespan=lifespan,
)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "cepraea-video-analysis-backend",
        "version": __version__,
    }
