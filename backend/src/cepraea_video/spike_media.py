"""Read-only access to MP4 files in the local INC-001 media directory."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

from cepraea_video.config import get_runtime_paths


def resolve_media(media_path: str) -> Path | None:
    """Resolve a top-level MP4 name without allowing paths outside the media directory."""
    if Path(media_path).name != media_path or Path(media_path).suffix.lower() != ".mp4":
        return None

    media_dir = get_runtime_paths().media_dir.resolve()
    candidate = (media_dir / media_path).resolve()
    if candidate.parent != media_dir or not candidate.is_file():
        return None
    return candidate


def list_media() -> list[dict[str, str]]:
    media_dir = get_runtime_paths().media_dir
    if not media_dir.is_dir():
        return []
    return [
        {"media_path": entry.name, "url": f"/spike/media/{quote(entry.name, safe='')}"}
        for entry in sorted(media_dir.iterdir())
        if resolve_media(entry.name) is not None
    ]
