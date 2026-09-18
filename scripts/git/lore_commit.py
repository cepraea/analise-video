#!/usr/bin/env python3
"""Build, show, validate, and optionally use a commit message from observed facts."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from .validate_commit_message import validate
except ImportError:
    from validate_commit_message import validate


ROOT = Path(__file__).resolve().parents[2]


def message(args: argparse.Namespace) -> str:
    lines = [args.title, ""]
    if args.tested:
        lines.append("Tested: " + "; ".join(args.tested))
    else:
        lines.append("Not-tested: " + args.not_tested)
    for value in args.constraint:
        lines.append("Constraint: " + value)
    for value in args.rejected:
        lines.append("Rejected: " + value)
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title", required=True)
    evidence = parser.add_mutually_exclusive_group(required=True)
    evidence.add_argument("--tested", action="append")
    evidence.add_argument("--not-tested")
    parser.add_argument("--constraint", action="append", default=[])
    parser.add_argument("--rejected", action="append", default=[])
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--commit", action="store_true", help="commit the existing index after showing the message")
    args = parser.parse_args()
    repo = args.repo.resolve()
    staged = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=repo)
    if staged.returncode == 0:
        print("ERROR: index has no staged changes", file=sys.stderr)
        return 1
    if staged.returncode != 1:
        print(f"ERROR: cannot inspect index; Git exited {staged.returncode}", file=sys.stderr)
        return 1
    content = message(args)
    errors = validate(content)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(content, end="")
    if not args.commit:
        return 0
    with tempfile.NamedTemporaryFile("w", encoding="utf-8") as handle:
        handle.write(content)
        handle.flush()
        return subprocess.run(["git", "commit", "-F", handle.name], cwd=repo).returncode


if __name__ == "__main__":
    raise SystemExit(main())
