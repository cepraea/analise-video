#!/usr/bin/env python3
"""Require every available baseline binary to be indexed in LFS and recovered."""

from __future__ import annotations

import argparse
import codecs
import json
from pathlib import Path
import re
import subprocess

import yaml

if __package__:
    from .validate_baselines import (
        OBJECT_ROOT, REGISTRY_PATH, object_file_error, sha256, valid_manifest_location,
    )
else:
    from validate_baselines import (
        OBJECT_ROOT, REGISTRY_PATH, object_file_error, sha256, valid_manifest_location,
    )


TEXT_APPLICATIONS = {
    "application/json", "application/javascript", "application/yaml",
    "application/x-yaml", "application/xml", "application/toml", "application/sql",
}


def declares_binary(item: dict) -> bool:
    media = (item.get("media_type") or "").split(";", 1)[0].lower()
    if Path(item["path"]).suffix.lower() in {".pdf", ".png"}:
        return True
    return bool(media and not media.startswith("text/") and media not in TEXT_APPLICATIONS
                and media != "application/octet-stream" and not media.endswith(("+json", "+xml")))


def is_binary(item: dict, path: Path) -> bool:
    """Honor binary declarations; inspect all bytes when metadata is ambiguous."""
    if declares_binary(item):
        return True
    decoder = codecs.getincrementaldecoder("utf-8")()
    with path.open("rb") as handle:
        header = handle.read(8)
        if header.startswith((b"%PDF-", b"\x89PNG\r\n\x1a\n")):
            return True
        handle.seek(0)
        try:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                if b"\0" in chunk:
                    return True
                decoder.decode(chunk)
            decoder.decode(b"", final=True)
        except UnicodeError:
            return True
    return False


def expected_binaries(repo: Path) -> tuple[set[str], list[str]]:
    """Resolve only exact objects referenced by manifests; never scan archive/."""
    registry = yaml.safe_load((repo / REGISTRY_PATH).read_text(encoding="utf-8"))
    expected: set[str] = set()
    errors: list[str] = []
    binary_by_digest: dict[str, bool] = {}
    for record in registry["baselines"]:
        if not valid_manifest_location(repo, record.get("manifest")):
            errors.append(f"{record['id']}: invalid manifest location")
            continue
        manifest_path = repo / record["manifest"]
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        items = list(manifest.get("sources", [])) + list(manifest.get("controls", []))
        missing: set[str] = set()
        if record["id"] == "G0":
            promotion = yaml.safe_load((repo / record["promotion"]).read_text(encoding="utf-8"))
            missing = {item["sha256"] for item in promotion["missing_historical_objects"]}
            for line in manifest_path.with_name("G0-CONTROL-SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
                digest, logical_path = line.split(maxsplit=1)
                items.append({"sha256": digest, "path": logical_path.lstrip("* ")})
        for item in items:
            digest = item["sha256"]
            if digest in missing:
                continue  # Preserve G0's explicit historical incompleteness.
            directory = repo / OBJECT_ROOT
            if error := object_file_error(directory, digest):
                errors.append(f"{record['id']}: {error}")
                continue
            path = directory / digest
            # A binary declaration in any revision must not be hidden by a text alias.
            if digest not in binary_by_digest or declares_binary(item):
                binary_by_digest[digest] = is_binary(item, path)
            if binary_by_digest[digest]:
                expected.add(f"{OBJECT_ROOT}/{digest}")
    return expected, errors


def validate(repo: Path) -> list[str]:
    def git(*args: str) -> bytes:
        return subprocess.check_output(["git", *args], cwd=repo, stderr=subprocess.PIPE)

    try:
        expected, errors = expected_binaries(repo)
        listing = json.loads(git("lfs", "ls-files", "--json"))
        files = listing.get("files") or []  # Git LFS emits null for an empty index.
        if not files:
            errors.append("no LFS objects found; baseline binaries must be tracked")
        by_name = {entry["name"]: entry for entry in files}
        for name in sorted(expected):
            entry = by_name.get(name)
            if entry is None:
                errors.append(f"baseline binary is not indexed in LFS: {name}; track this exact SHA-256 path and stage it again")
                continue
            if entry.get("oid") != Path(name).name:
                errors.append(f"LFS OID differs from baseline SHA-256: {name}")
            pointer = git("show", f":{name}")
            match = re.fullmatch(
                rb"version https://git-lfs.github.com/spec/v1\noid sha256:([0-9a-f]{64})\nsize ([0-9]+)\n",
                pointer,
            )
            if (match is None or match[1].decode() != entry.get("oid")
                    or int(match[2]) != entry.get("size")):
                errors.append(f"baseline binary lacks a matching LFS pointer in the index: {name}")

        for entry in files:
            name = entry["name"]
            path = repo / name
            if Path(name).is_absolute() or ".." in Path(name).parts or not path.resolve().is_relative_to(repo.resolve()):
                errors.append(f"invalid LFS path: {name}")
                continue
            if entry.get("oid_type") != "sha256" or path.is_symlink() or not path.is_file():
                errors.append(f"invalid or missing recovered LFS object: {name}")
                continue
            if path.stat().st_size != entry["size"] or sha256(path) != entry["oid"]:
                errors.append(f"recovered LFS bytes differ from pointer: {name}")
        return errors
    except (subprocess.CalledProcessError, OSError, RuntimeError, UnicodeError,
            ValueError, KeyError, TypeError, yaml.YAMLError) as exc:
        return [f"cannot verify baseline LFS coverage and recovery: {exc}"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    errors = validate(Path(args.repo).resolve())
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("LFS valid: every available baseline binary is indexed and recovered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
