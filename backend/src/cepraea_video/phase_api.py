"""HTTP API for manual possession and phase classification in INC-003."""

from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, model_validator

from cepraea_video.catalog_storage import (
    CatalogNotFoundError,
    CatalogRelationError,
    database_path,
)
from cepraea_video.phase_storage import (
    MINIMUM_PHASES,
    PhaseClassificationExistsError,
    create_phase_classification,
    get_phase_classification,
)

router = APIRouter(prefix="/catalog", tags=["inc-003-phase-classification"])


class PhaseTemporalReferenceInput(BaseModel):
    video_source_id: str = Field(min_length=1)
    start_ms: int = Field(ge=0)
    end_ms: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_interval(self) -> "PhaseTemporalReferenceInput":
        if self.end_ms <= self.start_ms:
            raise ValueError("end_ms deve ser maior que start_ms")
        return self


class PhaseSegmentInput(BaseModel):
    team_role: Literal["POSSESSION_TEAM", "ANALYZED_TEAM"]
    phase: str = Field(min_length=1)
    temporal_references: list[PhaseTemporalReferenceInput] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_phase(self) -> "PhaseSegmentInput":
        if not self.phase.strip():
            raise ValueError("phase não pode estar vazia")
        return self


class PhaseClassificationInput(BaseModel):
    possession_team: str = Field(min_length=1)
    analyzed_team: str = Field(min_length=1)
    phase_segments: list[PhaseSegmentInput] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_teams(self) -> "PhaseClassificationInput":
        if not self.possession_team.strip() or not self.analyzed_team.strip():
            raise ValueError("As equipes não podem estar vazias")
        return self


@router.get("/phase-values")
def get_phase_values() -> dict[str, list[str]]:
    return {"minimum_values": list(MINIMUM_PHASES)}


@router.post("/lances/{lance_id}/phase-classification", status_code=201)
def post_phase_classification(
    lance_id: str, data: PhaseClassificationInput
) -> dict[str, Any]:
    try:
        return create_phase_classification(
            database_path(),
            lance_id,
            data.possession_team,
            data.analyzed_team,
            [segment.model_dump() for segment in data.phase_segments],
        )
    except CatalogNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except CatalogRelationError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except PhaseClassificationExistsError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.get("/lances/{lance_id}/phase-classification")
def get_lance_phase_classification(lance_id: str) -> dict[str, Any]:
    classification = get_phase_classification(database_path(), lance_id)
    if classification is None:
        raise HTTPException(status_code=404, detail="Classificação não encontrada")
    return classification
