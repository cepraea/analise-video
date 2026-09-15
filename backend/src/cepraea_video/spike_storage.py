"""Disposable SQLite storage for the INC-001 architecture spike.

This table is not the canonical LANCE or VideoSource model.
"""

from __future__ import annotations

import sqlite3
from contextlib import closing
from dataclasses import asdict, dataclass
from pathlib import Path

from cepraea_video.config import get_runtime_paths

_INTERVAL_COLUMNS = "id, media_path, start_ms, end_ms, created_at"


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
    connection.execute("PRAGMA foreign_keys = ON")
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
                    ),
                    status TEXT NOT NULL DEFAULT 'ATIVO'
                        CHECK (status IN ('ATIVO', 'EXCLUÍDO')),
                    deletion_reason TEXT
                        CHECK (deletion_reason IS NULL OR length(trim(deletion_reason)) > 0),
                    deleted_at TEXT
                )
                """
            )
            # INC-001 databases already contain intervals. Add only missing columns;
            # never rebuild the table or replace its existing rows and IDs.
            columns = {
                row["name"]
                for row in connection.execute("PRAGMA table_info(spike_intervals)")
            }
            if "status" not in columns:
                connection.execute(
                    """ALTER TABLE spike_intervals ADD COLUMN status TEXT NOT NULL
                    DEFAULT 'ATIVO' CHECK (status IN ('ATIVO', 'EXCLUÍDO'))"""
                )
            if "deletion_reason" not in columns:
                connection.execute(
                    """ALTER TABLE spike_intervals ADD COLUMN deletion_reason TEXT
                    CHECK (deletion_reason IS NULL OR length(trim(deletion_reason)) > 0)"""
                )
            if "deleted_at" not in columns:
                connection.execute(
                    "ALTER TABLE spike_intervals ADD COLUMN deleted_at TEXT"
                )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS spike_interval_versions (
                    interval_id INTEGER NOT NULL REFERENCES spike_intervals(id)
                        ON DELETE RESTRICT,
                    version INTEGER NOT NULL CHECK (version >= 1),
                    start_ms INTEGER NOT NULL CHECK (start_ms >= 0),
                    end_ms INTEGER NOT NULL CHECK (end_ms > start_ms),
                    changed_at TEXT NOT NULL DEFAULT (
                        strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
                    ),
                    PRIMARY KEY (interval_id, version)
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
                f"SELECT {_INTERVAL_COLUMNS} FROM spike_intervals WHERE id = ?",
                (cursor.lastrowid,),
            ).fetchone()
    assert row is not None
    return SpikeInterval(**dict(row))


def list_intervals(path: Path) -> list[SpikeInterval]:
    with closing(_connect(path)) as connection:
        rows = connection.execute(
            f"SELECT {_INTERVAL_COLUMNS} FROM spike_intervals WHERE status = 'ATIVO' ORDER BY id"
        ).fetchall()
    return [SpikeInterval(**dict(row)) for row in rows]


def update_interval(path: Path, interval_id: int, start_ms: int, end_ms: int) -> SpikeInterval | None:
    if start_ms < 0 or end_ms <= start_ms:
        raise ValueError("Os limites do intervalo são inválidos")
    with closing(_connect(path)) as connection:
        with connection:
            previous = connection.execute(
                f"SELECT {_INTERVAL_COLUMNS} FROM spike_intervals WHERE id = ? AND status = 'ATIVO'",
                (interval_id,),
            ).fetchone()
            if previous is None:
                return None
            if (previous["start_ms"], previous["end_ms"]) != (start_ms, end_ms):
                connection.execute(
                    """
                    INSERT INTO spike_interval_versions (interval_id, version, start_ms, end_ms)
                    VALUES (?, COALESCE((SELECT MAX(version) + 1 FROM spike_interval_versions
                                         WHERE interval_id = ?), 1), ?, ?)
                    """,
                    (interval_id, interval_id, previous["start_ms"], previous["end_ms"]),
                )
                connection.execute(
                    "UPDATE spike_intervals SET start_ms = ?, end_ms = ? WHERE id = ?",
                    (start_ms, end_ms, interval_id),
                )
            current = connection.execute(
                f"SELECT {_INTERVAL_COLUMNS} FROM spike_intervals WHERE id = ?",
                (interval_id,),
            ).fetchone()
    assert current is not None
    return SpikeInterval(**dict(current))


def delete_interval(path: Path, interval_id: int, reason: str) -> bool:
    reason = reason.strip()
    if not reason:
        raise ValueError("O motivo da exclusão é obrigatório")
    with closing(_connect(path)) as connection:
        with connection:
            cursor = connection.execute(
                """
                UPDATE spike_intervals
                SET status = 'EXCLUÍDO', deletion_reason = ?,
                    deleted_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
                WHERE id = ? AND status = 'ATIVO'
                """,
                (reason, interval_id),
            )
    return cursor.rowcount == 1


def list_deleted_intervals(path: Path) -> list[dict[str, int | str]]:
    with closing(_connect(path)) as connection:
        rows = connection.execute(
            """
            SELECT id, media_path, start_ms, end_ms, created_at,
                   status, deletion_reason, deleted_at
            FROM spike_intervals WHERE status = 'EXCLUÍDO' ORDER BY id
            """
        ).fetchall()
    return [dict(row) for row in rows]


def list_interval_versions(path: Path, interval_id: int) -> list[dict[str, int | str]]:
    with closing(_connect(path)) as connection:
        rows = connection.execute(
            """
            SELECT interval_id, version, start_ms, end_ms, changed_at
            FROM spike_interval_versions WHERE interval_id = ? ORDER BY version
            """,
            (interval_id,),
        ).fetchall()
    return [dict(row) for row in rows]
