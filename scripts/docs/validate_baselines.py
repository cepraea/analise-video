#!/usr/bin/env python3
"""Validate baseline lineage, manifests and content-addressed objects."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import subprocess

import yaml


REGISTRY_PATH = "docs/evidence/ssot-migration/BASELINES.yaml"
BASELINE_ROOT = "docs/evidence/ssot-migration/baselines/"


def validate_lineage(records: list[dict]) -> list[str]:
    """Every successor must reach G0, never itself or a cycle."""
    errors: list[str] = []
    by_id = {record.get("id"): record for record in records}
    if "G0" not in by_id:
        errors.append("baseline lineage has no G0 root")
    elif by_id["G0"].get("predecessor") is not None:
        errors.append("G0 root must not have a predecessor")
    for baseline_id in by_id:
        visited: set[str] = set()
        current = baseline_id
        while current != "G0":
            if current in visited:
                errors.append(f"{baseline_id}: cyclic baseline lineage at {current}")
                break
            visited.add(current)
            if current not in by_id:
                errors.append(f"{baseline_id}: unknown predecessor {current}; lineage does not reach G0")
                break
            current = by_id[current].get("predecessor")
    return errors


def validate_immutability(repo: Path, base_ref: str) -> list[str]:
    """Compare published records and snapshot directories to a trusted Git base."""
    if base_ref == "0" * 40:  # GitHub's initial-push sentinel: no prior publication.
        return []
    def git(*args: str) -> bytes:
        return subprocess.check_output(["git", *args], cwd=repo, stderr=subprocess.PIPE)

    try:
        base = git("rev-parse", "--verify", f"{base_ref}^{{commit}}").decode().strip()
        registry_exists = git("ls-tree", "--name-only", base, "--", REGISTRY_PATH)
        if not registry_exists:
            return []  # Initial introduction of the baseline registry.
        previous = yaml.safe_load(git("show", f"{base}:{REGISTRY_PATH}"))
        current_path = repo / REGISTRY_PATH
        if not current_path.is_file():
            return ["published baseline registry removed"]
        current = yaml.safe_load(current_path.read_text(encoding="utf-8"))
        current_records = {record["id"]: record for record in current["baselines"]}
        errors: list[str] = []
        for record in previous["baselines"]:
            baseline_id = record["id"]
            if record.get("immutable") is not True:
                errors.append(f"{baseline_id}: base publication is not marked immutable")
            if current_records.get(baseline_id) != record:
                errors.append(f"{baseline_id}: published baseline record changed or removed; publish a successor")
            manifest = Path(record["manifest"])
            if not manifest.as_posix().startswith(BASELINE_ROOT) or ".." in manifest.parts:
                errors.append(f"{baseline_id}: invalid published manifest location")
                continue
            directory = manifest.parent.as_posix() + "/"
            changed = git("diff", "--name-only", "-z", base, "--", directory)
            untracked = git("ls-files", "--others", "--exclude-standard", "-z", "--", directory)
            for path in set((changed + untracked).decode().split("\0")) - {""}:
                errors.append(f"{baseline_id}: immutable snapshot changed: {path}; publish a successor")
        return errors
    except (subprocess.CalledProcessError, OSError, KeyError, TypeError, yaml.YAMLError) as exc:
        return [f"cannot verify baseline immutability against {base_ref}: {exc}"]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate(repo: Path, base_ref: str | None = None) -> list[str]:
    errors: list[str] = []
    index_path = repo / REGISTRY_PATH
    index = yaml.safe_load(index_path.read_text(encoding="utf-8"))
    records = index.get("baselines", [])
    ids = [item.get("id") for item in records]
    if len(ids) != len(set(ids)):
        errors.append("duplicate baseline IDs")
    errors.extend(validate_lineage(records))
    if base_ref is not None:
        errors.extend(validate_immutability(repo, base_ref))

    object_dir = repo / "archive/ssot/objects/sha256"
    verified_objects: set[str] = set()
    for record in records:
        if record.get("immutable") is not True:
            errors.append(f"{record['id']}: published baseline must be immutable")
        manifest_path = repo / record["manifest"]
        if not manifest_path.exists():
            errors.append(f"{record['id']}: manifest missing")
            continue
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        if record["id"] == "G0":
            items = list(manifest.get("sources", []))
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
            metadata = manifest.get("baseline", {})
            for field in ("id", "predecessor", "completeness"):
                if metadata.get(field) != record.get(field):
                    errors.append(f"{record['id']}: manifest {field} differs from registry")

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
        if record["id"] != "G0" and record.get("completeness") == "COMPLETE" and record.get("predecessor") is None:
            errors.append(f"{record['id']}: successor marked COMPLETE without predecessor")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--base-ref", help="trusted pre-change Git revision; required in CI")
    args = parser.parse_args()
    errors = validate(Path(args.repo).resolve(), args.base_ref)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Baselines valid: lineage, manifests and available objects verified")
    if args.base_ref is None:
        print("NOTE: cross-revision immutability was not checked; pass --base-ref to check it")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
