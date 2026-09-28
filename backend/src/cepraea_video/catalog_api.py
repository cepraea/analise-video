"""HTTP API for the canonical INC-002 catalog."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, model_validator

from cepraea_video.catalog_storage import (
    CatalogNotFoundError,
    CatalogRelationError,
    create_competition,
    create_game,
    create_lance,
    create_video_source,
    database_path,
    get_lance,
    list_competitions,
    list_games,
    list_video_sources,
)
from cepraea_video.local_media import resolve_media

router = APIRouter(prefix="/catalog", tags=["inc-002-catalog"])


class CompetitionInput(BaseModel):
    name: str = Field(min_length=1)


class GameInput(BaseModel):
    competition_id: str = Field(min_length=1)
    name: str = Field(min_length=1)


class VideoSourceInput(BaseModel):
    game_id: str = Field(min_length=1)
    media_path: str = Field(min_length=1)


class TemporalReferenceInput(BaseModel):
    video_source_id: str = Field(min_length=1)
    start_ms: int = Field(ge=0)
    end_ms: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_interval(self) -> "TemporalReferenceInput":
        if self.end_ms <= self.start_ms:
            raise ValueError("end_ms deve ser maior que start_ms")
        return self


class LanceInput(BaseModel):
    game_id: str = Field(min_length=1)
    temporal_references: list[TemporalReferenceInput] = Field(min_length=1)


def _not_found(error: CatalogNotFoundError) -> HTTPException:
    return HTTPException(status_code=404, detail=str(error))


@router.post("/competitions", status_code=201)
def post_competition(data: CompetitionInput) -> dict[str, Any]:
    if not data.name.strip():
        raise HTTPException(status_code=422, detail="name não pode estar vazio")
    return create_competition(database_path(), data.name)


@router.get("/competitions")
def get_competitions() -> list[dict[str, Any]]:
    return list_competitions(database_path())


@router.post("/games", status_code=201)
def post_game(data: GameInput) -> dict[str, Any]:
    if not data.name.strip():
        raise HTTPException(status_code=422, detail="name não pode estar vazio")
    try:
        return create_game(database_path(), data.competition_id, data.name)
    except CatalogNotFoundError as error:
        raise _not_found(error) from error


@router.get("/games")
def get_games(competition_id: str | None = None) -> list[dict[str, Any]]:
    return list_games(database_path(), competition_id)


@router.post("/video-sources", status_code=201)
def post_video_source(data: VideoSourceInput) -> dict[str, Any]:
    media = resolve_media(data.media_path)
    if media is None:
        raise HTTPException(
            status_code=422,
            detail="media_path deve nomear um MP4 existente no diretório de mídia local",
        )
    try:
        return create_video_source(database_path(), data.game_id, media.name)
    except CatalogNotFoundError as error:
        raise _not_found(error) from error


@router.get("/video-sources")
def get_video_sources(game_id: str | None = None) -> list[dict[str, Any]]:
    return list_video_sources(database_path(), game_id)


@router.post("/lances", status_code=201)
def post_lance(data: LanceInput) -> dict[str, Any]:
    try:
        return create_lance(
            database_path(),
            data.game_id,
            [reference.model_dump() for reference in data.temporal_references],
        )
    except CatalogNotFoundError as error:
        raise _not_found(error) from error
    except CatalogRelationError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.get("/lances/{lance_id}")
def get_catalog_lance(lance_id: str) -> dict[str, Any]:
    lance = get_lance(database_path(), lance_id)
    if lance is None:
        raise HTTPException(status_code=404, detail="Lance não encontrado")
    return lance
