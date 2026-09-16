#!/usr/bin/env python3
"""Validate baseline lineage, manifests and content-addressed objects."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import yaml


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate(repo: Path) -> list[str]:
    errors: list[str] = []
    index_path = repo / "docs/evidence/ssot-migration/BASELINES.yaml"
    index = yaml.safe_load(index_path.read_text(encoding="utf-8"))
    records = index.get("baselines", [])
    ids = [item.get("id") for item in records]
    if len(ids) != len(set(ids)):
        errors.append("duplicate baseline IDs")

    object_dir = repo / "archive/ssot/objects/sha256"
    verified_objects: set[str] = set()
    for record in records:
        manifest_path = repo / record["manifest"]
        if not manifest_path.exists():
            errors.append(f"{record['id']}: manifest missing")
            continue
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        if record["id"] == "G0":
            items = manifest.get("sources", [])
            promotion = yaml.safe_load((repo / record["promotion"]).read_text(encoding="utf-8"))
            declared_missing = {item["sha256"] for item in promotion["missing_historical_objects"]}
            control_sums = manifest_path.with_name("G0-CONTROL-SHA256SUMS.txt")
            for line in control_sums.read_text(encoding="utf-8").splitlines():
                digest, logical_path = line.split(maxsplit=1)
                items.append({"sha256": digest, "path": logical_path.lstrip("* ")})
            if promotion["completeness"] != record["completeness"]:
                errors.append("G0 completeness differs between index and promotion")
            if len(items) != promotion["declared_items"]:
                errors.append("G0 declared item count differs from source and control manifests")
        else:
            items = manifest.get("sources", []) + manifest.get("controls", [])
            declared_missing = set()
            predecessor = record.get("predecessor")
            if predecessor not in ids:
                errors.append(f"{record['id']}: unknown predecessor {predecessor}")

        for item in items:
            digest = item["sha256"]
            object_path = object_dir / digest
            if digest in declared_missing:
                continue
            if not object_path.exists():
                errors.append(f"{record['id']}: object missing for {item['path']}: {digest}")
                continue
            if digest not in verified_objects:
                actual = sha256(object_path)
                if actual != digest or object_path.name != actual:
                    errors.append(f"corrupt content-addressed object: {object_path}")
                verified_objects.add(digest)

        if record.get("completeness") == "COMPLETE" and declared_missing:
            errors.append(f"{record['id']}: COMPLETE baseline declares missing objects")
        if record.get("completeness") == "COMPLETE" and record.get("predecessor") is None:
            errors.append(f"{record['id']}: successor marked COMPLETE without predecessor")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    errors = validate(Path(args.repo).resolve())
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Baselines valid: lineage, manifests and available objects verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
