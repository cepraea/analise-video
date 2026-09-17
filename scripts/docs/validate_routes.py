#!/usr/bin/env python3
"""Validate the minimum-context route registry."""

from __future__ import annotations

import argparse
from fnmatch import fnmatchcase
from pathlib import Path, PurePosixPath

import yaml


REQUIRED_EXCLUSIONS = {"archive/**", ".local/drafts/**"}


def operational_path(
    repo: Path, name: str, exclusions: list[str], *, must_exist: bool = True,
    allow_directory: bool = False,
) -> Path:
    if not isinstance(name, str) or not name or "\\" in name:
        raise ValueError(f"invalid operational path: {name}")
    relative = PurePosixPath(name)
    if relative.is_absolute() or ".." in relative.parts or "{" in name or "}" in name:
        raise ValueError(f"operational path must be relative and concrete: {name}")
    if any(part in {"archive", ".local", ".git", "node_modules", ".venv", "__pycache__", "dist", "build"} for part in relative.parts):
        raise ValueError(f"operational path enters excluded tree: {name}")
    for pattern in exclusions:
        base = pattern[:-3] if pattern.endswith("/**") else pattern
        if fnmatchcase(name, pattern) or name.rstrip("/") == base:
            raise ValueError(f"operational path enters excluded tree: {name}")
    candidate = repo.resolve()
    for part in relative.parts:
        candidate /= part
        if candidate.is_symlink():
            raise ValueError(f"operational path uses a symlink: {name}")
    if must_exist and not candidate.exists():
        raise ValueError(f"operational path does not exist: {name}")
    if candidate.exists() and not candidate.is_file() and not (allow_directory and candidate.is_dir()):
        raise ValueError(f"operational path must be a regular file: {name}")
    return candidate


def validate(repo: Path, route_file: Path) -> list[str]:
    errors: list[str] = []
    data = yaml.safe_load(route_file.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return ["ROUTES must be a YAML mapping"]
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    defaults = data.get("defaults", {})
    exclusions = set(defaults.get("exclude", []))
    missing_exclusions = sorted(REQUIRED_EXCLUSIONS - exclusions)
    if missing_exclusions:
        errors.append(f"required exclusions missing: {', '.join(missing_exclusions)}")
    if defaults.get("archive_access") != "exact_object_only":
        errors.append("archive_access must be exact_object_only")
    if not {"conflicting_authority", "missing_required_document", "broken_id_reference"}.issubset(defaults.get("stop_if", [])):
        errors.append("required stop conditions missing")

    def check_path(name: str, label: str) -> None:
        try:
            operational_path(repo, name, list(exclusions), allow_directory=True)
        except ValueError as exc:
            errors.append(f"{label}: {exc}")

    check_path(data.get("policy"), "policy")
    if "AGENTS.md" not in defaults.get("always", []):
        errors.append("defaults.always must include AGENTS.md")
    for item in defaults.get("always", []):
        check_path(item, "always")

    routes = data.get("routes")
    if not isinstance(routes, dict) or not routes:
        return errors + ["routes must be a non-empty mapping"]

    for route_name, route in routes.items():
        if not isinstance(route, dict):
            errors.append(f"{route_name}: route must be a mapping")
            continue
        required = route.get("required", [])
        if not required:
            errors.append(f"{route_name}: required must not be empty")
        for item in required:
            check_path(item, route_name)
        for item in route.get("optional", []):
            if not isinstance(item, dict) or not item.get("when"):
                errors.append(f"{route_name}: optional path needs an explicit when condition")
                continue
            path = item.get("path")
            if path == "docs/context/packs/{increment}.md" and item["when"] == "generated_pack_exists":
                continue
            check_path(path, f"{route_name}: optional")
        for item in route.get("allow", []):
            if item.startswith("archive/") and "{sha256}" not in item:
                errors.append(f"{route_name}: archive access must select an exact SHA-256 object: {item}")

    audit = routes.get("source_audit", {})
    allowed = set(audit.get("allow", []))
    if "archive/ssot/objects/sha256/{sha256}" not in allowed:
        errors.append("source_audit must allow only an exact content-addressed archive object")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("route_file", nargs="?", default="docs/context/ROUTES.yaml")
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    route_file = (repo / args.route_file).resolve()
    errors = validate(repo, route_file)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"ROUTES valid: {route_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
