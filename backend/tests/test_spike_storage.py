import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from cepraea_video.main import app


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
    assert columns == ["id", "media_path", "start_ms", "end_ms", "created_at"]

    with TestClient(app) as reopened_client:
        response = reopened_client.get("/spike/intervals")

    assert response.status_code == 200
    assert response.json() == [saved]
    assert media.read_bytes() == original_bytes
    assert list(media_dir.iterdir()) == [media]


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
