import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from cepraea_video.main import app


def _create_lance(client: TestClient, media_name: str) -> tuple[dict, dict]:
    competition = client.post(
        "/catalog/competitions", json={"name": "Liga 2026"}
    ).json()
    game = client.post(
        "/catalog/games",
        json={"competition_id": competition["id"], "name": "Jogo"},
    ).json()
    source = client.post(
        "/catalog/video-sources",
        json={"game_id": game["id"], "media_path": media_name},
    ).json()
    lance = client.post(
        "/catalog/lances",
        json={
            "game_id": game["id"],
            "temporal_references": [
                {
                    "video_source_id": source["id"],
                    "start_ms": 1000,
                    "end_ms": 5000,
                }
            ],
        },
    ).json()
    return source, lance


def test_manual_phase_classification_survives_restart_with_independent_overlap(
    tmp_path: Path, monkeypatch
) -> None:
    data_dir = tmp_path / "data"
    media_dir = tmp_path / "media"
    media_dir.mkdir()
    media = media_dir / "jogo.mp4"
    media.write_bytes(b"immutable video")
    monkeypatch.setenv("CEPRAEA_DATA_DIR", str(data_dir))
    monkeypatch.setenv("CEPRAEA_MEDIA_DIR", str(media_dir))

    with TestClient(app) as client:
        source, lance = _create_lance(client, media.name)
        minimum_values = client.get("/catalog/phase-values")
        saved = client.post(
            f"/catalog/lances/{lance['id']}/phase-classification",
            json={
                "possession_team": "Adversária",
                "analyzed_team": "CEPRAEA",
                "phase_segments": [
                    {
                        "team_role": "POSSESSION_TEAM",
                        "phase": "Transição Ofensiva",
                        "temporal_references": [
                            {
                                "video_source_id": source["id"],
                                "start_ms": 1000,
                                "end_ms": 2200,
                            }
                        ],
                    },
                    {
                        "team_role": "ANALYZED_TEAM",
                        "phase": "Transição Defensiva",
                        "temporal_references": [
                            {
                                "video_source_id": source["id"],
                                "start_ms": 1000,
                                "end_ms": 2600,
                            }
                        ],
                    },
                    {
                        "team_role": "POSSESSION_TEAM",
                        "phase": "Ataque Posicionado",
                        "temporal_references": [
                            {
                                "video_source_id": source["id"],
                                "start_ms": 2200,
                                "end_ms": 5000,
                            }
                        ],
                    },
                    {
                        "team_role": "ANALYZED_TEAM",
                        "phase": "Defesa Posicionada",
                        "temporal_references": [
                            {
                                "video_source_id": source["id"],
                                "start_ms": 2600,
                                "end_ms": 5000,
                            }
                        ],
                    },
                ],
            },
        )

    assert minimum_values.status_code == 200
    assert minimum_values.json()["minimum_values"] == [
        "Transição Ofensiva",
        "Ataque Posicionado",
        "Transição Defensiva",
        "Defesa Posicionada",
    ]
    assert saved.status_code == 201
    saved_classification = saved.json()
    assert saved_classification["possession_team"] == "Adversária"
    assert saved_classification["analyzed_team"] == "CEPRAEA"
    assert [
        segment["team_name"] for segment in saved_classification["phase_segments"]
    ] == ["Adversária", "CEPRAEA", "Adversária", "CEPRAEA"]

    with TestClient(app) as client:
        duplicate = client.post(
            f"/catalog/lances/{lance['id']}/phase-classification",
            json={
                "possession_team": "CEPRAEA",
                "analyzed_team": "Adversária",
                "phase_segments": [
                    {
                        "team_role": "POSSESSION_TEAM",
                        "phase": "Outra fase",
                        "temporal_references": [
                            {
                                "video_source_id": source["id"],
                                "start_ms": 1200,
                                "end_ms": 2000,
                            }
                        ],
                    }
                ],
            },
        )

    assert duplicate.status_code == 409

    with TestClient(app) as reopened:
        recovered = reopened.get(
            f"/catalog/lances/{lance['id']}/phase-classification"
        )

    assert recovered.status_code == 200
    assert recovered.json() == saved_classification
    with sqlite3.connect(data_dir / "inc002.sqlite3") as connection:
        assert connection.execute("PRAGMA quick_check").fetchone()[0] == "ok"
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []


def test_phase_classification_rejects_bounds_outside_lance_atomically(
    tmp_path: Path, monkeypatch
) -> None:
    data_dir = tmp_path / "data"
    media_dir = tmp_path / "media"
    media_dir.mkdir()
    media = media_dir / "jogo.mp4"
    media.write_bytes(b"immutable video")
    monkeypatch.setenv("CEPRAEA_DATA_DIR", str(data_dir))
    monkeypatch.setenv("CEPRAEA_MEDIA_DIR", str(media_dir))

    with TestClient(app) as client:
        source, lance = _create_lance(client, media.name)
        response = client.post(
            f"/catalog/lances/{lance['id']}/phase-classification",
            json={
                "possession_team": "CEPRAEA",
                "analyzed_team": "CEPRAEA",
                "phase_segments": [
                    {
                        "team_role": "POSSESSION_TEAM",
                        "phase": "Transição Ofensiva",
                        "temporal_references": [
                            {
                                "video_source_id": source["id"],
                                "start_ms": 900,
                                "end_ms": 2200,
                            }
                        ],
                    }
                ],
            },
        )

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "O segmento deve estar contido em uma referência temporal do lance"
    )
    with sqlite3.connect(data_dir / "inc002.sqlite3") as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM lance_phase_classifications"
        ).fetchone()[0] == 0
        assert connection.execute(
            "SELECT COUNT(*) FROM phase_segments"
        ).fetchone()[0] == 0
