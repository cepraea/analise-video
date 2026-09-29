"""SQLite persistence for manual possession and phase classification."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any, Iterable
from uuid import uuid4

from cepraea_video.catalog_storage import (
    CatalogNotFoundError,
    CatalogRelationError,
)

POSSESSION_TEAM = "POSSESSION_TEAM"
ANALYZED_TEAM = "ANALYZED_TEAM"
MINIMUM_PHASES = (
    "Transição Ofensiva",
    "Ataque Posicionado",
    "Transição Defensiva",
    "Defesa Posicionada",
)


class PhaseClassificationExistsError(ValueError):
    """Raised when a lance already has a manual classification."""


def _connect(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


def initialize_phase_storage(path: Path) -> None:
    with closing(_connect(path)) as connection:
        with connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS lance_phase_classifications (
                    lance_id TEXT PRIMARY KEY REFERENCES lances(id)
                        ON DELETE RESTRICT,
                    possession_team TEXT NOT NULL
                        CHECK (length(trim(possession_team)) > 0),
                    analyzed_team TEXT NOT NULL
                        CHECK (length(trim(analyzed_team)) > 0),
                    created_at TEXT NOT NULL DEFAULT (
                        strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
                    )
                );

                CREATE TABLE IF NOT EXISTS phase_segments (
                    id TEXT PRIMARY KEY,
                    lance_id TEXT NOT NULL REFERENCES lances(id)
                        ON DELETE RESTRICT,
                    team_role TEXT NOT NULL CHECK (
                        team_role IN ('POSSESSION_TEAM', 'ANALYZED_TEAM')
                    ),
                    phase TEXT NOT NULL CHECK (length(trim(phase)) > 0),
                    record_order INTEGER NOT NULL CHECK (record_order >= 0),
                    created_at TEXT NOT NULL DEFAULT (
                        strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
                    ),
                    UNIQUE (id, lance_id),
                    UNIQUE (lance_id, record_order)
                );

                CREATE TABLE IF NOT EXISTS phase_segment_temporal_references (
                    id TEXT PRIMARY KEY,
                    phase_segment_id TEXT NOT NULL,
                    lance_id TEXT NOT NULL,
                    video_source_id TEXT NOT NULL,
                    game_id TEXT NOT NULL,
                    start_ms INTEGER NOT NULL CHECK (start_ms >= 0),
                    end_ms INTEGER NOT NULL CHECK (end_ms > start_ms),
                    created_at TEXT NOT NULL DEFAULT (
                        strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
                    ),
                    FOREIGN KEY (phase_segment_id, lance_id)
                        REFERENCES phase_segments(id, lance_id) ON DELETE RESTRICT,
                    FOREIGN KEY (lance_id, game_id)
                        REFERENCES lances(id, game_id) ON DELETE RESTRICT,
                    FOREIGN KEY (video_source_id, game_id)
                        REFERENCES video_sources(id, game_id) ON DELETE RESTRICT
                );

                CREATE INDEX IF NOT EXISTS phase_segments_by_lance
                    ON phase_segments(lance_id, record_order);
                CREATE INDEX IF NOT EXISTS phase_segment_references_by_segment
                    ON phase_segment_temporal_references(phase_segment_id);
                """
            )


def _read_phase_classification(
    connection: sqlite3.Connection, lance_id: str
) -> dict[str, Any] | None:
    classification = connection.execute(
        "SELECT * FROM lance_phase_classifications WHERE lance_id = ?",
        (lance_id,),
    ).fetchone()
    if classification is None:
        return None

    segment_rows = connection.execute(
        """
        SELECT * FROM phase_segments
        WHERE lance_id = ?
        ORDER BY record_order
        """,
        (lance_id,),
    ).fetchall()
    segments: list[dict[str, Any]] = []
    for row in segment_rows:
        segment = dict(row)
        references = connection.execute(
            """
            SELECT id, phase_segment_id, video_source_id,
                   start_ms, end_ms, created_at
            FROM phase_segment_temporal_references
            WHERE phase_segment_id = ?
            ORDER BY created_at, id
            """,
            (segment["id"],),
        ).fetchall()
        segment["team_name"] = classification[
            "possession_team"
            if segment["team_role"] == POSSESSION_TEAM
            else "analyzed_team"
        ]
        segment["temporal_references"] = [dict(reference) for reference in references]
        segments.append(segment)

    return {**dict(classification), "phase_segments": segments}


def get_phase_classification(path: Path, lance_id: str) -> dict[str, Any] | None:
    with closing(_connect(path)) as connection:
        return _read_phase_classification(connection, lance_id)


def create_phase_classification(
    path: Path,
    lance_id: str,
    possession_team: str,
    analyzed_team: str,
    phase_segments: Iterable[dict[str, Any]],
) -> dict[str, Any]:
    pending_segments = list(phase_segments)
    if not pending_segments:
        raise ValueError("Ao menos um segmento de fase é obrigatório")

    with closing(_connect(path)) as connection:
        with connection:
            lance = connection.execute(
                "SELECT game_id FROM lances WHERE id = ?", (lance_id,)
            ).fetchone()
            if lance is None:
                raise CatalogNotFoundError("Lance não encontrado")
            if connection.execute(
                "SELECT 1 FROM lance_phase_classifications WHERE lance_id = ?",
                (lance_id,),
            ).fetchone():
                raise PhaseClassificationExistsError(
                    "O lance já possui classificação manual"
                )

            connection.execute(
                """
                INSERT INTO lance_phase_classifications (
                    lance_id, possession_team, analyzed_team
                ) VALUES (?, ?, ?)
                """,
                (lance_id, possession_team.strip(), analyzed_team.strip()),
            )
            for record_order, segment in enumerate(pending_segments):
                segment_id = _new_id("phase")
                connection.execute(
                    """
                    INSERT INTO phase_segments (
                        id, lance_id, team_role, phase, record_order
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        segment_id,
                        lance_id,
                        segment["team_role"],
                        str(segment["phase"]).strip(),
                        record_order,
                    ),
                )
                for reference in segment["temporal_references"]:
                    _insert_segment_reference(
                        connection,
                        lance_id,
                        lance["game_id"],
                        segment_id,
                        reference,
                    )

            result = _read_phase_classification(connection, lance_id)
    assert result is not None
    return result


def _insert_segment_reference(
    connection: sqlite3.Connection,
    lance_id: str,
    game_id: str,
    segment_id: str,
    reference: dict[str, Any],
) -> None:
    source_id = str(reference["video_source_id"])
    start_ms = int(reference["start_ms"])
    end_ms = int(reference["end_ms"])
    enclosing_reference = connection.execute(
        """
        SELECT 1 FROM temporal_references
        WHERE lance_id = ? AND video_source_id = ?
          AND start_ms <= ? AND end_ms >= ?
        """,
        (lance_id, source_id, start_ms, end_ms),
    ).fetchone()
    if enclosing_reference is None:
        raise CatalogRelationError(
            "O segmento deve estar contido em uma referência temporal do lance"
        )
    connection.execute(
        """
        INSERT INTO phase_segment_temporal_references (
            id, phase_segment_id, lance_id, video_source_id,
            game_id, start_ms, end_ms
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            _new_id("phase_time"),
            segment_id,
            lance_id,
            source_id,
            game_id,
            start_ms,
            end_ms,
        ),
    )
