from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, model_validator
from starlette.responses import FileResponse

from cepraea_video import __version__
from cepraea_video.config import ensure_runtime_directories
from cepraea_video.spike_media import list_media, resolve_media
from cepraea_video.spike_storage import (
    database_path,
    delete_interval,
    initialize_storage,
    list_deleted_intervals,
    list_interval_versions,
    list_intervals,
    save_interval,
    update_interval,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    ensure_runtime_directories()
    initialize_storage(database_path())
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


class SpikeIntervalInput(BaseModel):
    media_path: str = Field(min_length=1)
    start_ms: int = Field(ge=0)
    end_ms: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_interval(self) -> "SpikeIntervalInput":
        if not self.media_path.strip():
            raise ValueError("media_path não pode estar vazio")
        if self.end_ms <= self.start_ms:
            raise ValueError("end_ms deve ser maior que start_ms")
        return self


class SpikeIntervalUpdate(BaseModel):
    start_ms: int = Field(ge=0)
    end_ms: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_interval(self) -> "SpikeIntervalUpdate":
        if self.end_ms <= self.start_ms:
            raise ValueError("end_ms deve ser maior que start_ms")
        return self


class SpikeIntervalDeletion(BaseModel):
    reason: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_reason(self) -> "SpikeIntervalDeletion":
        if not self.reason.strip():
            raise ValueError("O motivo da exclusão é obrigatório")
        return self


@app.post("/spike/intervals", status_code=201, tags=["inc-001-spike"])
def create_spike_interval(interval: SpikeIntervalInput) -> dict[str, int | str]:
    if resolve_media(interval.media_path) is None:
        raise HTTPException(
            status_code=422,
            detail="media_path deve nomear um MP4 existente no diretório de mídia local",
        )
    return save_interval(
        database_path(), interval.media_path, interval.start_ms, interval.end_ms
    ).to_dict()


@app.get("/spike/intervals", tags=["inc-001-spike"])
def get_spike_intervals() -> list[dict[str, int | str]]:
    return [interval.to_dict() for interval in list_intervals(database_path())]


@app.patch("/spike/intervals/{interval_id}", tags=["inc-001-spike"])
def patch_spike_interval(
    interval_id: int, interval: SpikeIntervalUpdate
) -> dict[str, int | str]:
    updated = update_interval(
        database_path(), interval_id, interval.start_ms, interval.end_ms
    )
    if updated is None:
        raise HTTPException(status_code=404, detail="Intervalo ativo não encontrado")
    return updated.to_dict()


@app.delete("/spike/intervals/{interval_id}", tags=["inc-001-spike"])
def delete_spike_interval(
    interval_id: int, deletion: SpikeIntervalDeletion
) -> dict[str, str]:
    if not delete_interval(database_path(), interval_id, deletion.reason):
        raise HTTPException(status_code=404, detail="Intervalo ativo não encontrado")
    return {"status": "EXCLUÍDO"}


@app.get("/spike/intervals/deleted", tags=["inc-001-spike"])
def get_deleted_spike_intervals() -> list[dict[str, int | str]]:
    return list_deleted_intervals(database_path())


@app.get("/spike/intervals/{interval_id}/versions", tags=["inc-001-spike"])
def get_spike_interval_versions(interval_id: int) -> list[dict[str, int | str]]:
    return list_interval_versions(database_path(), interval_id)


@app.get("/spike/media", tags=["inc-001-spike"])
def get_spike_media() -> list[dict[str, str]]:
    return list_media()


@app.get("/spike/media/{media_path}", tags=["inc-001-spike"])
def get_spike_media_file(media_path: str) -> FileResponse:
    path = resolve_media(media_path)
    if path is None:
        raise HTTPException(status_code=404, detail="MP4 local não encontrado")
    return FileResponse(path, media_type="video/mp4")
