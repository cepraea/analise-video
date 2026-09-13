from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


_REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class RuntimePaths:
    data_dir: Path
    media_dir: Path


def get_runtime_paths() -> RuntimePaths:
    """Resolve local runtime paths without requiring secrets or cloud services."""
    default_root = _REPOSITORY_ROOT / ".local"
    data_dir = Path(os.getenv("CEPRAEA_DATA_DIR", default_root / "data")).expanduser()
    media_dir = Path(os.getenv("CEPRAEA_MEDIA_DIR", default_root / "media")).expanduser()
    return RuntimePaths(data_dir=data_dir, media_dir=media_dir)


def ensure_runtime_directories(paths: RuntimePaths | None = None) -> RuntimePaths:
    resolved = paths or get_runtime_paths()
    resolved.data_dir.mkdir(parents=True, exist_ok=True)
    resolved.media_dir.mkdir(parents=True, exist_ok=True)
    return resolved
