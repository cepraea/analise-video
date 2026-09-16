#!/usr/bin/env python3
"""Validate the minimum-context route registry."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml


REQUIRED_EXCLUSIONS = {"archive/**", ".local/drafts/**"}


def validate(repo: Path, route_file: Path) -> list[str]:
    errors: list[str] = []
    data = yaml.safe_load(route_file.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    defaults = data.get("defaults", {})
    exclusions = set(defaults.get("exclude", []))
    missing_exclusions = sorted(REQUIRED_EXCLUSIONS - exclusions)
    if missing_exclusions:
        errors.append(f"required exclusions missing: {', '.join(missing_exclusions)}")
    if defaults.get("archive_access") != "exact_object_only":
        errors.append("archive_access must be exact_object_only")

    routes = data.get("routes")
    if not isinstance(routes, dict) or not routes:
        return errors + ["routes must be a non-empty mapping"]

    for route_name, route in routes.items():
        required = route.get("required", [])
        if not required:
            errors.append(f"{route_name}: required must not be empty")
        for item in required:
            if item.startswith("archive/") or item.startswith(".local/drafts/"):
                errors.append(f"{route_name}: operational required path enters excluded tree: {item}")
                continue
            if "{" in item or item.endswith("/"):
                candidate = repo / item.rstrip("/")
            else:
                candidate = repo / item
            if "{" not in item and not candidate.exists():
                errors.append(f"{route_name}: required path does not exist: {item}")
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
