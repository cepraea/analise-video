import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from cepraea_video.main import app
from cepraea_video.spike_storage import initialize_storage, list_intervals, save_interval


def test_interval_survives_application_restart(tmp_path: Path, monkeypatch) -> None:
    data_dir = tmp_path / "data"
    monkeypatch.setenv("CEPRAEA_DATA_DIR", str(data_dir))
    media_dir = tmp_path / "media"
    media_dir.mkdir()
    monkeypatch.setenv("CEPRAEA_MEDIA_DIR", str(media_dir))
    media = media_dir / "video.mp4"
    media.write_bytes(b"original media bytes")
    original_bytes = media.read_bytes()

    with TestClient(app) as client:
        response = client.post(
            "/spike/intervals",
            json={"media_path": media.name, "start_ms": 1200, "end_ms": 3400},
        )
        assert response.status_code == 201
        saved = response.json()

    db_path = data_dir / "inc001.sqlite3"
    assert db_path.is_file()
    assert saved["id"] == 1
    assert (saved["media_path"], saved["start_ms"], saved["end_ms"]) == (
        media.name,
        1200,
        3400,
    )
    assert saved["created_at"].endswith("Z")

    with sqlite3.connect(db_path) as connection:
        columns = [row[1] for row in connection.execute("PRAGMA table_info(spike_intervals)")]
        version_columns = [
            row[1] for row in connection.execute("PRAGMA table_info(spike_interval_versions)")
        ]
    assert columns == [
        "id", "media_path", "start_ms", "end_ms", "created_at",
        "status", "deletion_reason", "deleted_at",
    ]
    assert version_columns == [
        "interval_id", "version", "start_ms", "end_ms", "changed_at",
    ]

    with TestClient(app) as reopened_client:
        response = reopened_client.get("/spike/intervals")

    assert response.status_code == 200
    assert response.json() == [saved]
    assert media.read_bytes() == original_bytes
    assert list(media_dir.iterdir()) == [media]


def test_existing_intervals_keep_ids_and_values_after_migration(tmp_path: Path) -> None:
    db_path = tmp_path / "inc001.sqlite3"
    original_rows = [
        (2, "first.mp4", 1200, 3400, "2026-09-13T10:00:00.000Z"),
        (9, "second.mp4", 7500, 8400, "2026-09-13T11:00:00.000Z"),
    ]
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE spike_intervals (
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
        connection.executemany(
            "INSERT INTO spike_intervals VALUES (?, ?, ?, ?, ?)", original_rows
        )

    initialize_storage(db_path)
    initialize_storage(db_path)

    with sqlite3.connect(db_path) as connection:
        migrated_rows = connection.execute(
            """SELECT id, media_path, start_ms, end_ms, created_at,
                      status, deletion_reason, deleted_at
               FROM spike_intervals ORDER BY id"""
        ).fetchall()
        versions = connection.execute(
            "SELECT * FROM spike_interval_versions"
        ).fetchall()
        integrity = connection.execute("PRAGMA quick_check").fetchone()[0]

    assert migrated_rows == [row + ("ATIVO", None, None) for row in original_rows]
    assert versions == []
    assert integrity == "ok"
    assert [interval.id for interval in list_intervals(db_path)] == [2, 9]
    assert save_interval(db_path, "third.mp4", 10000, 20000).id == 10


@pytest.mark.parametrize("start_ms,end_ms", [(3400, 1200), (3400, 3400)])
def test_invalid_interval_is_rejected(
    tmp_path: Path, monkeypatch, start_ms: int, end_ms: int
) -> None:
    monkeypatch.setenv("CEPRAEA_DATA_DIR", str(tmp_path / "data"))
    media_dir = tmp_path / "media"
    media_dir.mkdir()
    (media_dir / "video.mp4").write_bytes(b"original media bytes")
    monkeypatch.setenv("CEPRAEA_MEDIA_DIR", str(media_dir))

    with TestClient(app) as client:
        response = client.post(
            "/spike/intervals",
            json={"media_path": "video.mp4", "start_ms": start_ms, "end_ms": end_ms},
        )
        intervals = client.get("/spike/intervals")

    assert response.status_code == 422
    assert intervals.json() == []


def test_edit_keeps_identity_and_records_prior_versions_after_restart(
    tmp_path: Path, monkeypatch
) -> None:
    data_dir = tmp_path / "data"
    media_dir = tmp_path / "media"
    media_dir.mkdir()
    (media_dir / "video.mp4").write_bytes(b"original media bytes")
    monkeypatch.setenv("CEPRAEA_DATA_DIR", str(data_dir))
    monkeypatch.setenv("CEPRAEA_MEDIA_DIR", str(media_dir))

    with TestClient(app) as client:
        original = client.post(
            "/spike/intervals",
            json={"media_path": "video.mp4", "start_ms": 1200, "end_ms": 3400},
        ).json()
        first = client.patch(
            f"/spike/intervals/{original['id']}",
            json={"start_ms": 1300, "end_ms": 3500},
        )
        second = client.patch(
            f"/spike/intervals/{original['id']}",
            json={"start_ms": 1400, "end_ms": 3600},
        )
        no_change = client.patch(
            f"/spike/intervals/{original['id']}",
            json={"start_ms": 1400, "end_ms": 3600},
        )

    assert (first.status_code, second.status_code, no_change.status_code) == (200, 200, 200)
    assert (second.json()["id"], second.json()["media_path"], second.json()["created_at"]) == (
        original["id"], original["media_path"], original["created_at"],
    )
    with TestClient(app) as reopened:
        assert reopened.get("/spike/intervals").json() == [second.json()]
        versions_response = reopened.get(f"/spike/intervals/{original['id']}/versions")
    assert versions_response.status_code == 200
    versions = versions_response.json()
    assert [(v["version"], v["start_ms"], v["end_ms"]) for v in versions] == [
        (1, 1200, 3400), (2, 1300, 3500),
    ]
    assert all(v["changed_at"].endswith("Z") for v in versions)


def test_invalid_edit_and_missing_interval_do_not_create_versions(
    tmp_path: Path, monkeypatch
) -> None:
    data_dir = tmp_path / "data"
    media_dir = tmp_path / "media"
    media_dir.mkdir()
    (media_dir / "video.mp4").write_bytes(b"original media bytes")
    monkeypatch.setenv("CEPRAEA_DATA_DIR", str(data_dir))
    monkeypatch.setenv("CEPRAEA_MEDIA_DIR", str(media_dir))

    with TestClient(app) as client:
        saved = client.post(
            "/spike/intervals",
            json={"media_path": "video.mp4", "start_ms": 1200, "end_ms": 3400},
        ).json()
        for start_ms, end_ms in [(3400, 3400), (3500, 3400), (-1, 3400)]:
            assert client.patch(
                f"/spike/intervals/{saved['id']}",
                json={"start_ms": start_ms, "end_ms": end_ms},
            ).status_code == 422
        assert client.patch(
            "/spike/intervals/999",
            json={"start_ms": 1000, "end_ms": 2000},
        ).status_code == 404
        assert client.get(f"/spike/intervals/{saved['id']}/versions").json() == []
        assert client.get("/spike/intervals").json() == [saved]


def test_soft_delete_requires_reason_and_remains_auditable(
    tmp_path: Path, monkeypatch
) -> None:
    data_dir = tmp_path / "data"
    media_dir = tmp_path / "media"
    media_dir.mkdir()
    media = media_dir / "video.mp4"
    media.write_bytes(b"original media bytes")
    monkeypatch.setenv("CEPRAEA_DATA_DIR", str(data_dir))
    monkeypatch.setenv("CEPRAEA_MEDIA_DIR", str(media_dir))

    with TestClient(app) as client:
        saved = client.post(
            "/spike/intervals",
            json={"media_path": "video.mp4", "start_ms": 1200, "end_ms": 3400},
        ).json()
        assert client.request("DELETE", f"/spike/intervals/{saved['id']}", json={"reason": "  "}).status_code == 422
        assert client.get("/spike/intervals").json() == [saved]
        response = client.request(
            "DELETE", f"/spike/intervals/{saved['id']}", json={"reason": "Marcação inválida"}
        )
        assert response.status_code == 200
        assert client.get("/spike/intervals").json() == []
        assert client.patch(
            f"/spike/intervals/{saved['id']}",
            json={"start_ms": 1300, "end_ms": 3500},
        ).status_code == 404
        assert client.request(
            "DELETE", f"/spike/intervals/{saved['id']}", json={"reason": "De novo"}
        ).status_code == 404

    with TestClient(app) as reopened:
        deleted = reopened.get("/spike/intervals/deleted").json()
        assert reopened.get("/spike/intervals").json() == []
    assert len(deleted) == 1
    assert {key: deleted[0][key] for key in saved} == saved
    assert deleted[0]["status"] == "EXCLUÍDO"
    assert deleted[0]["deletion_reason"] == "Marcação inválida"
    assert deleted[0]["deleted_at"].endswith("Z")
    assert media.read_bytes() == b"original media bytes"
