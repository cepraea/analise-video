from pathlib import Path

from fastapi.testclient import TestClient

from cepraea_video.config import RuntimePaths, ensure_runtime_directories
from cepraea_video.main import app


def test_health_endpoint_starts_application() -> None:
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "cepraea-video-analysis-backend"


def test_runtime_directories_are_created_outside_versioned_content(tmp_path: Path) -> None:
    paths = RuntimePaths(
        data_dir=tmp_path / "data",
        media_dir=tmp_path / "media",
    )

    resolved = ensure_runtime_directories(paths)

    assert resolved.data_dir.is_dir()
    assert resolved.media_dir.is_dir()
