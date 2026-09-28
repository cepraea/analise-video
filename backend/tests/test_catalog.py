import hashlib
import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from cepraea_video.main import app


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _create_game(client: TestClient, competition_name: str, game_name: str) -> dict:
    competition = client.post(
        "/catalog/competitions", json={"name": competition_name}
    )
    assert competition.status_code == 201
    game = client.post(
        "/catalog/games",
        json={"competition_id": competition.json()["id"], "name": game_name},
    )
    assert game.status_code == 201
    return game.json()


def test_catalog_survives_restart_with_multiple_sources_and_traceability(
    tmp_path: Path, monkeypatch
) -> None:
    data_dir = tmp_path / "data"
    media_dir = tmp_path / "media"
    media_dir.mkdir()
    first_media = media_dir / "camera-principal.mp4"
    second_media = media_dir / "camera-fundo.mp4"
    first_media.write_bytes(b"first immutable video")
    second_media.write_bytes(b"second immutable video")
    original_hashes = {_sha256(first_media), _sha256(second_media)}
    monkeypatch.setenv("CEPRAEA_DATA_DIR", str(data_dir))
    monkeypatch.setenv("CEPRAEA_MEDIA_DIR", str(media_dir))

    with TestClient(app) as client:
        game = _create_game(client, "Liga 2026", "CEPRAEA x Visitante")
        sources = [
            client.post(
                "/catalog/video-sources",
                json={"game_id": game["id"], "media_path": media.name},
            ).json()
            for media in (first_media, second_media)
        ]
        response = client.post(
            "/catalog/lances",
            json={
                "game_id": game["id"],
                "temporal_references": [
                    {
                        "video_source_id": sources[0]["id"],
                        "start_ms": 1200,
                        "end_ms": 3400,
                    },
                    {
                        "video_source_id": sources[1]["id"],
                        "start_ms": 1500,
                        "end_ms": 3700,
                    },
                ],
            },
        )
        assert response.status_code == 201
        saved_lance = response.json()

    assert saved_lance["id"].startswith("lance_")
    assert all(source["id"].startswith("source_") for source in sources)
    assert all(source["id"] != source["media_path"] for source in sources)

    db_path = data_dir / "inc002.sqlite3"
    with sqlite3.connect(db_path) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        integrity = connection.execute("PRAGMA quick_check").fetchone()[0]
        foreign_key_issues = connection.execute("PRAGMA foreign_key_check").fetchall()
    assert {
        "competitions",
        "games",
        "video_sources",
        "lances",
        "temporal_references",
    }.issubset(tables)
    assert integrity == "ok"
    assert foreign_key_issues == []

    with TestClient(app) as reopened:
        recovered_competitions = reopened.get("/catalog/competitions")
        recovered_games = reopened.get(
            "/catalog/games", params={"competition_id": game["competition_id"]}
        )
        recovered = reopened.get(f"/catalog/lances/{saved_lance['id']}")
        recovered_sources = reopened.get(
            "/catalog/video-sources", params={"game_id": game["id"]}
        )

    assert recovered_competitions.status_code == 200
    assert recovered_competitions.json()[0]["id"] == game["competition_id"]
    assert recovered_games.json() == [game]
    assert recovered.status_code == 200
    assert recovered.json() == saved_lance
    assert sorted(recovered_sources.json(), key=lambda source: source["id"]) == sorted(
        sources, key=lambda source: source["id"]
    )
    assert {
        reference["video_source_id"]
        for reference in recovered.json()["temporal_references"]
    } == {source["id"] for source in sources}
    assert {
        reference["media_path"]
        for reference in recovered.json()["temporal_references"]
    } == {first_media.name, second_media.name}
    assert {_sha256(first_media), _sha256(second_media)} == original_hashes
    assert sorted(path.name for path in media_dir.iterdir()) == sorted(
        [first_media.name, second_media.name]
    )


def test_lance_rejects_source_from_another_game_without_partial_write(
    tmp_path: Path, monkeypatch
) -> None:
    data_dir = tmp_path / "data"
    media_dir = tmp_path / "media"
    media_dir.mkdir()
    media = media_dir / "video.mp4"
    media.write_bytes(b"immutable video")
    monkeypatch.setenv("CEPRAEA_DATA_DIR", str(data_dir))
    monkeypatch.setenv("CEPRAEA_MEDIA_DIR", str(media_dir))

    with TestClient(app) as client:
        first_game = _create_game(client, "Competição A", "Jogo A")
        second_game = _create_game(client, "Competição B", "Jogo B")
        source = client.post(
            "/catalog/video-sources",
            json={"game_id": first_game["id"], "media_path": media.name},
        ).json()
        response = client.post(
            "/catalog/lances",
            json={
                "game_id": second_game["id"],
                "temporal_references": [
                    {
                        "video_source_id": source["id"],
                        "start_ms": 1000,
                        "end_ms": 2000,
                    }
                ],
            },
        )

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "Lance e fonte de vídeo devem pertencer ao mesmo jogo"
    )
    with sqlite3.connect(data_dir / "inc002.sqlite3") as connection:
        assert connection.execute("SELECT COUNT(*) FROM lances").fetchone()[0] == 0
        assert (
            connection.execute(
                "SELECT COUNT(*) FROM temporal_references"
            ).fetchone()[0]
            == 0
        )
    assert _sha256(media) == hashlib.sha256(b"immutable video").hexdigest()


def test_catalog_rejects_missing_media_and_invalid_temporal_reference(
    tmp_path: Path, monkeypatch
) -> None:
    media_dir = tmp_path / "media"
    media_dir.mkdir()
    monkeypatch.setenv("CEPRAEA_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("CEPRAEA_MEDIA_DIR", str(media_dir))

    with TestClient(app) as client:
        game = _create_game(client, "Competição", "Jogo")
        missing_media = client.post(
            "/catalog/video-sources",
            json={"game_id": game["id"], "media_path": "ausente.mp4"},
        )
        invalid_reference = client.post(
            "/catalog/lances",
            json={
                "game_id": game["id"],
                "temporal_references": [
                    {
                        "video_source_id": "source_ausente",
                        "start_ms": 2000,
                        "end_ms": 1000,
                    }
                ],
            },
        )

    assert missing_media.status_code == 422
    assert invalid_reference.status_code == 422
