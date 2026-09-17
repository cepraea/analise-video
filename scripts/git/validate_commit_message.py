#!/usr/bin/env python3
"""Validate the current commit message and its final Lore trailer block."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


TITLE = re.compile(r"^(?:feat|fix|docs|refactor|test|chore|build|ci|perf)(?:\([a-z0-9-]+\))?!?: .+\S$")
TRAILER = re.compile(r"^([A-Za-z][A-Za-z-]*):\s*(.*)$")
LORE = {"Tested", "Not-tested", "Constraint", "Rejected"}
STANDARD = {"Co-authored-by", "Signed-off-by", "Fixes", "Refs"}
GENERIC = {"n/a", "na", "none", "todo", "tbd", "unknown", "-"}


def validate(text: str) -> list[str]:
    errors: list[str] = []
    lines = text.rstrip("\n").splitlines()
    if not lines or not TITLE.fullmatch(lines[0]):
        errors.append("title must use Conventional Commit syntax")
    start = len(lines)
    while start and TRAILER.fullmatch(lines[start - 1]):
        start -= 1
    trailer_lines = lines[start:]
    parsed: dict[str, str] = {}
    for line in trailer_lines:
        key, value = TRAILER.fullmatch(line).groups()
        if key not in LORE | STANDARD:
            errors.append(f"unsupported trailer: {key}")
        if key in parsed:
            errors.append(f"duplicate trailer: {key}")
        parsed[key] = value.strip()
        if not value.strip() or value.strip().lower() in GENERIC:
            errors.append(f"trailer {key} needs a concrete value")
    for line in lines[1:start]:
        match = TRAILER.fullmatch(line)
        if match and match.group(1) in LORE:
            errors.append(f"Lore trailer outside final block: {match.group(1)}")
    if "Tested" not in parsed and "Not-tested" not in parsed:
        errors.append("final trailer block must contain Tested or Not-tested")
    if "Tested" in parsed and "Not-tested" in parsed:
        errors.append("use Tested or Not-tested, not both")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("message", type=Path)
    args = parser.parse_args()
    try:
        errors = validate(args.message.read_text(encoding="utf-8"))
    except OSError as exc:
        print(f"ERROR: cannot read commit message: {exc}", file=sys.stderr)
        return 1
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        return 1
    print(f"Commit message valid: {args.message}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
