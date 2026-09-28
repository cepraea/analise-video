"""Canonical SQLite catalog for the INC-002 domain entities."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any, Iterable
from uuid import uuid4

from cepraea_video.config import get_runtime_paths


class CatalogNotFoundError(ValueError):
    """Raised when a referenced catalog entity does not exist."""


class CatalogRelationError(ValueError):
    """Raised when catalog entities belong to incompatible parents."""


def database_path() -> Path:
    return get_runtime_paths().data_dir / "inc002.sqlite3"


def _connect(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


def initialize_catalog(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with closing(_connect(path)) as connection:
        with connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS competitions (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
                    created_at TEXT NOT NULL DEFAULT (
                        strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
                    )
                );

                CREATE TABLE IF NOT EXISTS games (
                    id TEXT PRIMARY KEY,
                    competition_id TEXT NOT NULL REFERENCES competitions(id)
                        ON DELETE RESTRICT,
                    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
                    created_at TEXT NOT NULL DEFAULT (
                        strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
                    )
                );

                CREATE TABLE IF NOT EXISTS video_sources (
                    id TEXT PRIMARY KEY,
                    game_id TEXT NOT NULL REFERENCES games(id) ON DELETE RESTRICT,
                    media_path TEXT NOT NULL CHECK (length(trim(media_path)) > 0),
                    created_at TEXT NOT NULL DEFAULT (
                        strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
                    ),
                    UNIQUE (id, game_id)
                );

                CREATE TABLE IF NOT EXISTS lances (
                    id TEXT PRIMARY KEY,
                    game_id TEXT NOT NULL REFERENCES games(id) ON DELETE RESTRICT,
                    created_at TEXT NOT NULL DEFAULT (
                        strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
                    ),
                    UNIQUE (id, game_id)
                );

                CREATE TABLE IF NOT EXISTS temporal_references (
                    id TEXT PRIMARY KEY,
                    lance_id TEXT NOT NULL,
                    video_source_id TEXT NOT NULL,
                    game_id TEXT NOT NULL,
                    start_ms INTEGER NOT NULL CHECK (start_ms >= 0),
                    end_ms INTEGER NOT NULL CHECK (end_ms > start_ms),
                    created_at TEXT NOT NULL DEFAULT (
                        strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
                    ),
                    FOREIGN KEY (lance_id, game_id) REFERENCES lances(id, game_id)
                        ON DELETE RESTRICT,
                    FOREIGN KEY (video_source_id, game_id)
                        REFERENCES video_sources(id, game_id) ON DELETE RESTRICT
                );

                CREATE INDEX IF NOT EXISTS games_by_competition
                    ON games(competition_id);
                CREATE INDEX IF NOT EXISTS video_sources_by_game
                    ON video_sources(game_id);
                CREATE INDEX IF NOT EXISTS lances_by_game ON lances(game_id);
                CREATE INDEX IF NOT EXISTS temporal_references_by_lance
                    ON temporal_references(lance_id);
                """
            )


def _insert_and_read(
    connection: sqlite3.Connection,
    table: str,
    entity_id: str,
    values: dict[str, object],
) -> dict[str, Any]:
    columns = ["id", *values]
    placeholders = ", ".join("?" for _ in columns)
    connection.execute(
        f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})",
        [entity_id, *values.values()],
    )
    row = connection.execute(
        f"SELECT * FROM {table} WHERE id = ?", (entity_id,)
    ).fetchone()
    assert row is not None
    return dict(row)


def create_competition(path: Path, name: str) -> dict[str, Any]:
    with closing(_connect(path)) as connection:
        with connection:
            return _insert_and_read(
                connection, "competitions", _new_id("cmp"), {"name": name.strip()}
            )


def create_game(
    path: Path, competition_id: str, name: str
) -> dict[str, Any]:
    with closing(_connect(path)) as connection:
        with connection:
            if not _exists(connection, "competitions", competition_id):
                raise CatalogNotFoundError("Competição não encontrada")
            return _insert_and_read(
                connection,
                "games",
                _new_id("game"),
                {"competition_id": competition_id, "name": name.strip()},
            )


def create_video_source(
    path: Path, game_id: str, media_path: str
) -> dict[str, Any]:
    with closing(_connect(path)) as connection:
        with connection:
            if not _exists(connection, "games", game_id):
                raise CatalogNotFoundError("Jogo não encontrado")
            return _insert_and_read(
                connection,
                "video_sources",
                _new_id("source"),
                {"game_id": game_id, "media_path": media_path},
            )


def _exists(connection: sqlite3.Connection, table: str, entity_id: str) -> bool:
    return (
        connection.execute(
            f"SELECT 1 FROM {table} WHERE id = ?", (entity_id,)
        ).fetchone()
        is not None
    )


def list_competitions(path: Path) -> list[dict[str, Any]]:
    return _list_rows(path, "SELECT * FROM competitions ORDER BY created_at, id", ())


def list_games(path: Path, competition_id: str | None) -> list[dict[str, Any]]:
    if competition_id is None:
        return _list_rows(path, "SELECT * FROM games ORDER BY created_at, id", ())
    return _list_rows(
        path,
        "SELECT * FROM games WHERE competition_id = ? ORDER BY created_at, id",
        (competition_id,),
    )


def list_video_sources(path: Path, game_id: str | None) -> list[dict[str, Any]]:
    if game_id is None:
        return _list_rows(
            path, "SELECT * FROM video_sources ORDER BY created_at, id", ()
        )
    return _list_rows(
        path,
        "SELECT * FROM video_sources WHERE game_id = ? ORDER BY created_at, id",
        (game_id,),
    )


def _list_rows(
    path: Path, statement: str, parameters: tuple[object, ...]
) -> list[dict[str, Any]]:
    with closing(_connect(path)) as connection:
        rows = connection.execute(statement, parameters).fetchall()
    return [dict(row) for row in rows]


def create_lance(
    path: Path, game_id: str, references: Iterable[dict[str, int | str]]
) -> dict[str, Any]:
    pending = list(references)
    if not pending:
        raise ValueError("Ao menos uma referência temporal é obrigatória")
    lance_id = _new_id("lance")
    with closing(_connect(path)) as connection:
        with connection:
            if not _exists(connection, "games", game_id):
                raise CatalogNotFoundError("Jogo não encontrado")
            _insert_and_read(
                connection, "lances", lance_id, {"game_id": game_id}
            )
            for reference in pending:
                source_id = str(reference["video_source_id"])
                source = connection.execute(
                    "SELECT game_id FROM video_sources WHERE id = ?", (source_id,)
                ).fetchone()
                if source is None:
                    raise CatalogNotFoundError("Fonte de vídeo não encontrada")
                if source["game_id"] != game_id:
                    raise CatalogRelationError(
                        "Lance e fonte de vídeo devem pertencer ao mesmo jogo"
                    )
                _insert_and_read(
                    connection,
                    "temporal_references",
                    _new_id("time"),
                    {
                        "lance_id": lance_id,
                        "video_source_id": source_id,
                        "game_id": game_id,
                        "start_ms": reference["start_ms"],
                        "end_ms": reference["end_ms"],
                    },
                )
            result = _read_lance(connection, lance_id)
    assert result is not None
    return result


def get_lance(path: Path, lance_id: str) -> dict[str, Any] | None:
    with closing(_connect(path)) as connection:
        return _read_lance(connection, lance_id)


def _read_lance(
    connection: sqlite3.Connection, lance_id: str
) -> dict[str, Any] | None:
    lance = connection.execute(
        "SELECT * FROM lances WHERE id = ?", (lance_id,)
    ).fetchone()
    if lance is None:
        return None
    references = connection.execute(
        """
        SELECT temporal_references.id, temporal_references.lance_id,
               temporal_references.video_source_id, video_sources.media_path,
               temporal_references.start_ms, temporal_references.end_ms,
               temporal_references.created_at
        FROM temporal_references
        JOIN video_sources ON video_sources.id = temporal_references.video_source_id
        WHERE temporal_references.lance_id = ?
        ORDER BY temporal_references.created_at, temporal_references.id
        """,
        (lance_id,),
    ).fetchall()
    return {**dict(lance), "temporal_references": [dict(row) for row in references]}
