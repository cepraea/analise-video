#!/usr/bin/env python3
"""Check scoped naming and physical-line rules for a selected Git view."""

from __future__ import annotations

import argparse
import ast
from fnmatch import fnmatchcase
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

import yaml


CONFIG = "docs/context/CODE_RULES.yaml"
SNAKE = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")
SCRIPT_STEM = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")
WEB_STEM = re.compile(r"^(?:[a-z][A-Za-z0-9]*|[A-Z][A-Za-z0-9]*)(?:\.(?:test|spec|config))?$")
KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ID_KEBAB = re.compile(r"^[A-Z]+-[0-9]+(?:-[a-z0-9]+)*$")
ADR = re.compile(r"^ADR-[0-9]{3}-[a-z0-9]+(?:-[a-z0-9]+)*$")
UPPER_HYPHEN = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+$")


def git(repo: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=repo)


def selected_paths(repo: Path, source: str, revision: str) -> list[str]:
    if source == "workspace":
        raw = git(repo, "ls-files", "-co", "--exclude-standard", "-z")
    elif source == "index":
        raw = git(repo, "ls-files", "--cached", "-z")
    else:
        raw = git(repo, "ls-tree", "-r", "--name-only", "-z", revision)
    return sorted({item.decode() for item in raw.split(b"\0") if item})


def read_bytes(repo: Path, path: str, source: str, revision: str) -> bytes:
    if source == "workspace":
        return (repo / path).read_bytes()
    selector = f":{path}" if source == "index" else f"{revision}:{path}"
    return git(repo, "show", selector)


def matches_any(path: str, patterns: list[str]) -> bool:
    return any(fnmatchcase(path, pattern) for pattern in patterns)


def validate_exception(item: dict, label: str) -> list[str]:
    required = ["path", "reason", "responsible", "review_when"]
    missing = [key for key in required if not item.get(key)]
    return [f"{label} exception lacks {', '.join(missing)}: {item.get('path', '<unknown>')}"] if missing else []


def naming_error(path: str, opaque: set[str]) -> str | None:
    value = PurePosixPath(path)
    stem = value.name
    suffix = value.suffix
    base = stem[: -len(suffix)] if suffix else stem
    if base.lower() in opaque:
        return "opaque file name"
    if path.startswith(("scripts/", "backend/", "tests/")) and suffix == ".py":
        if base == "__init__":
            return None
        return None if SCRIPT_STEM.fullmatch(base) else "Python file must use snake_case"
    if path.startswith("frontend/") and suffix in {".js", ".jsx", ".ts", ".tsx"}:
        return None if WEB_STEM.fullmatch(base) else "JS/TS file must use camelCase or PascalCase"
    if path.startswith("docs/architecture/") and base.startswith("ADR-"):
        return None if ADR.fullmatch(base) else "ADR must include ID and kebab-case slug"
    if path.startswith("docs/") and suffix in {".md", ".yaml", ".json"}:
        if value.parent == PurePosixPath("docs"):
            return None if re.fullmatch(r"[A-Z][A-Z0-9_]*", base) else "top-level canonical document must use UPPER_SNAKE_CASE"
        if path.startswith("docs/context/packs/"):
            return None if re.fullmatch(r"[A-Z]+-[0-9]+", base) else "context pack must use its stable ID"
        if re.fullmatch(r"[A-Z][A-Z0-9_]*", base) or UPPER_HYPHEN.fullmatch(base) or KEBAB.fullmatch(base) or ID_KEBAB.fullmatch(base):
            return None
        return "auxiliary document must use kebab-case, stable ID plus slug, or canonical UPPER_SNAKE_CASE"
    return None


def check(repo: Path, config_path: Path, source: str, revision: str) -> tuple[list[str], list[str]]:
    config_name = config_path.resolve().relative_to(repo.resolve()).as_posix()
    config = yaml.safe_load(read_bytes(repo, config_name, source, revision).decode())
    if not isinstance(config, dict) or config.get("schema_version") != 1:
        return ["CODE_RULES schema_version must be 1"], []
    manual = config["manual_code"]
    naming = config["naming"]
    errors: list[str] = []
    warnings: list[str] = []
    size_exceptions = {item.get("path"): item for item in manual.get("size_exceptions", [])}
    name_exceptions = {item.get("path"): item for item in naming.get("path_exceptions", [])}
    for item in [*size_exceptions.values(), *name_exceptions.values()]:
        errors.extend(validate_exception(item, "code rule"))
    paths = selected_paths(repo, source, revision)
    excluded = manual.get("exclude", [])
    opaque = set(naming.get("opaque_stems", []))
    for path in paths:
        if matches_any(path, excluded):
            continue
        if source == "workspace" and not (repo / path).exists():
            continue
        try:
            content = read_bytes(repo, path, source, revision)
        except (OSError, subprocess.CalledProcessError) as exc:
            errors.append(f"{path}: cannot read selected bytes: {exc}")
            continue
        issue = naming_error(path, opaque)
        if issue:
            if path in name_exceptions:
                warnings.append(f"{path}: naming exception: {issue}")
            else:
                errors.append(f"{path}: {issue}")
        if PurePosixPath(path).suffix not in set(manual["extensions"]):
            continue
        lines = len(content.splitlines())
        exception = size_exceptions.get(path)
        limit = exception.get("maximum_lines") if exception else manual["maximum_lines"]
        if not isinstance(limit, int) or limit < manual["maximum_lines"]:
            errors.append(f"{path}: invalid size exception limit")
        elif lines > limit:
            errors.append(f"{path}: {lines} physical lines exceeds limit {limit}")
        elif lines > manual["warning_lines"]:
            label = "explicit exception" if exception and lines > manual["maximum_lines"] else "modularization review"
            warnings.append(f"{path}: {lines} physical lines; {label}")

    for contract in config.get("function_prefix_contracts", []):
        path = contract.get("path")
        symbol = contract.get("symbol")
        prefixes = contract.get("allowed_prefixes", [])
        if not path or not symbol or not prefixes or not contract.get("behavior"):
            errors.append(f"invalid function prefix contract: {contract}")
            continue
        try:
            tree = ast.parse(read_bytes(repo, path, source, revision), filename=path)
        except (OSError, SyntaxError, subprocess.CalledProcessError) as exc:
            errors.append(f"{path}: cannot inspect function contract: {exc}")
            continue
        names = {node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
        if symbol not in names:
            errors.append(f"{path}: contracted function is absent: {symbol}")
        elif not any(symbol.startswith(prefix) for prefix in prefixes):
            errors.append(f"{path}:{symbol}: incompatible prefix; expected one of {', '.join(prefixes)}")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--config", default=CONFIG)
    parser.add_argument("--source", choices=["workspace", "index", "commit"], default="workspace")
    parser.add_argument("--revision", default="HEAD")
    args = parser.parse_args()
    repo = args.repo.resolve()
    try:
        errors, warnings = check(repo, repo / args.config, args.source, args.revision)
    except (KeyError, TypeError, ValueError, OSError, subprocess.CalledProcessError, yaml.YAMLError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        return 1
    print(f"Code rules valid for {args.source}: {len(warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
