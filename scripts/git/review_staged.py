#!/usr/bin/env python3
"""Review the Git index bytes with local, deterministic checks."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.context import build_code_graph  # noqa: E402
from scripts.docs import check_code_rules  # noqa: E402


SECRET_RULES = {
    "private-key": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "aws-access-key": re.compile(rb"\bAKIA[0-9A-Z]{16}\b"),
    "generic-api-key": re.compile(rb"(?i)\b(?:api[_-]?key|secret[_-]?key)\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{16,}"),
}


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, check=check)


def staged_paths(repo: Path, diff_filter: str = "ACMRD") -> list[str]:
    result = git(repo, "diff", "--cached", "--name-only", f"--diff-filter={diff_filter}", "-z")
    return [item.decode() for item in result.stdout.split(b"\0") if item]


def staged_bytes(repo: Path, path: str) -> bytes:
    return git(repo, "show", f":{path}").stdout


def review(repo: Path) -> tuple[list[str], list[str]]:
    errors, warnings = check_code_rules.check(
        repo, repo / check_code_rules.CONFIG, "index", "HEAD"
    )
    whitespace = git(repo, "diff", "--cached", "--check", check=False)
    if whitespace.returncode:
        errors.append("staged diff has whitespace errors")
    try:
        paths = staged_paths(repo)
    except subprocess.CalledProcessError as exc:
        return errors + [f"cannot enumerate staged paths: Git exited {exc.returncode}"], warnings
    config = None
    try:
        config = yaml.safe_load(build_code_graph.read(repo, build_code_graph.CONFIG, "index", "HEAD"))
        if not isinstance(config, dict) or config.get("schema_version") != 1:
            raise ValueError("GRAPH schema_version must be 1")
    except subprocess.CalledProcessError as exc:
        if any(path in {build_code_graph.CONFIG, *build_code_graph.EXTRACTORS} for path in paths):
            errors.append(f"staged code graph invalid: configuration unavailable (Git exited {exc.returncode})")
    except (ValueError, TypeError, yaml.YAMLError) as exc:
        errors.append(f"staged code graph invalid: {exc}")
    try:
        if config is None:
            graph_changed = False
        else:
            graph_changed = any(
                path in {build_code_graph.CONFIG, *build_code_graph.EXTRACTORS}
                or build_code_graph.corpus_path(path, config)
                for path in paths
            )
        if graph_changed:
            build_code_graph.check(repo, "index", "HEAD")
    except (OSError, subprocess.CalledProcessError, ValueError, KeyError, TypeError, json.JSONDecodeError, yaml.YAMLError) as exc:
        errors.append(f"staged code graph invalid: {exc}")
    for path in staged_paths(repo, "ACMR"):
        try:
            content = staged_bytes(repo, path)
        except subprocess.CalledProcessError as exc:
            errors.append(f"{path}: cannot read staged bytes: Git exited {exc.returncode}")
            continue
        for rule, pattern in SECRET_RULES.items():
            if pattern.search(content):
                errors.append(f"{path}: possible secret detected ({rule}); value omitted")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        errors, warnings = review(args.repo.resolve())
    except (OSError, subprocess.CalledProcessError, ValueError, KeyError, TypeError) as exc:
        print(f"ERROR: staged review failed: {exc}", file=sys.stderr)
        return 1
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        return 1
    print(f"Staged review valid: {len(warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
