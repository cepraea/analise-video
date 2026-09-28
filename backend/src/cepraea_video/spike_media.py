"""Read-only access to MP4 files in the local INC-001 media directory."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

from cepraea_video.config import get_runtime_paths
from cepraea_video.local_media import resolve_media as resolve_local_media


def resolve_media(media_path: str) -> Path | None:
    """Preserve the INC-001 media resolver contract."""
    return resolve_local_media(media_path)


def list_media() -> list[dict[str, str]]:
    media_dir = get_runtime_paths().media_dir
    if not media_dir.is_dir():
        return []
    return [
        {"media_path": entry.name, "url": f"/spike/media/{quote(entry.name, safe='')}"}
        for entry in sorted(media_dir.iterdir())
        if resolve_media(entry.name) is not None
    ]
