from pathlib import Path

from fastapi.testclient import TestClient

from cepraea_video.main import app


def test_local_mp4_is_listed_and_supports_byte_ranges(tmp_path: Path, monkeypatch) -> None:
    media_dir = tmp_path / "media"
    media_dir.mkdir()
    media = media_dir / "partida 1.mp4"
    content = b"0123456789abcdef"
    media.write_bytes(content)
    (media_dir / "notes.txt").write_text("not a video")
    monkeypatch.setenv("CEPRAEA_MEDIA_DIR", str(media_dir))
    monkeypatch.setenv("CEPRAEA_DATA_DIR", str(tmp_path / "data"))

    with TestClient(app) as client:
        media_list = client.get("/spike/media")
        response = client.get("/spike/media/partida%201.mp4", headers={"Range": "bytes=4-7"})

    assert media_list.json() == [
        {"media_path": media.name, "url": "/spike/media/partida%201.mp4"}
    ]
    assert response.status_code == 206
    assert response.headers["content-type"] == "video/mp4"
    assert response.headers["content-range"] == "bytes 4-7/16"
    assert response.content == content[4:8]
    assert media.read_bytes() == content


def test_media_outside_local_directory_is_not_exposed(tmp_path: Path, monkeypatch) -> None:
    media_dir = tmp_path / "media"
    media_dir.mkdir()
    (media_dir / "outside.mp4").symlink_to(tmp_path / "secret.mp4")
    (tmp_path / "secret.mp4").write_bytes(b"secret")
    monkeypatch.setenv("CEPRAEA_MEDIA_DIR", str(media_dir))
    monkeypatch.setenv("CEPRAEA_DATA_DIR", str(tmp_path / "data"))

    with TestClient(app) as client:
        media_list = client.get("/spike/media")
        video = client.get("/spike/media/outside.mp4")
        interval = client.post(
            "/spike/intervals",
            json={"media_path": "outside.mp4", "start_ms": 1000, "end_ms": 2000},
        )

    assert media_list.json() == []
    assert video.status_code == 404
    assert interval.status_code == 422
