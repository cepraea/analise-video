"""Disposable SQLite storage for the INC-001 architecture spike.

This table is not the canonical LANCE or VideoSource model.
"""

from __future__ import annotations

import sqlite3
from contextlib import closing
from dataclasses import asdict, dataclass
from pathlib import Path

from cepraea_video.config import get_runtime_paths


@dataclass(frozen=True)
class SpikeInterval:
    id: int
    media_path: str
    start_ms: int
    end_ms: int
    created_at: str

    def to_dict(self) -> dict[str, int | str]:
        return asdict(self)


def database_path() -> Path:
    return get_runtime_paths().data_dir / "inc001.sqlite3"


def _connect(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_storage(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with closing(_connect(path)) as connection:
        with connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS spike_intervals (
                    id INTEGER PRIMARY KEY,
                    media_path TEXT NOT NULL CHECK (length(trim(media_path)) > 0),
                    start_ms INTEGER NOT NULL CHECK (start_ms >= 0),
                    end_ms INTEGER NOT NULL CHECK (end_ms > start_ms),
                    created_at TEXT NOT NULL DEFAULT (
                        strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
                    )
                )
                """
            )


def save_interval(
    path: Path, media_path: str, start_ms: int, end_ms: int
) -> SpikeInterval:
    with closing(_connect(path)) as connection:
        with connection:
            cursor = connection.execute(
                """
                INSERT INTO spike_intervals (media_path, start_ms, end_ms)
                VALUES (?, ?, ?)
                """,
                (media_path, start_ms, end_ms),
            )
            row = connection.execute(
                "SELECT * FROM spike_intervals WHERE id = ?", (cursor.lastrowid,)
            ).fetchone()
    assert row is not None
    return SpikeInterval(**dict(row))


def list_intervals(path: Path) -> list[SpikeInterval]:
    with closing(_connect(path)) as connection:
        rows = connection.execute(
            "SELECT * FROM spike_intervals ORDER BY id"
        ).fetchall()
    return [SpikeInterval(**dict(row)) for row in rows]
