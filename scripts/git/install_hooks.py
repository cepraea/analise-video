#!/usr/bin/env python3
"""Install or remove CEPRAEA hooks without overwriting existing hooks."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


HOOKS = ("pre-commit", "commit-msg")
ALIAS = "!python3 scripts/git/lore_commit.py --commit"


def git_dir(repo: Path) -> Path:
    value = subprocess.check_output(["git", "rev-parse", "--git-dir"], cwd=repo, text=True).strip()
    path = Path(value)
    return path if path.is_absolute() else repo / path


def expected_target(repo: Path, name: str) -> Path:
    return (repo / ".githooks" / name).resolve()


def managed(path: Path, target: Path) -> bool:
    return path.is_symlink() and path.resolve() == target


def install(repo: Path) -> list[str]:
    directory = git_dir(repo) / "hooks"
    directory.mkdir(parents=True, exist_ok=True)
    collisions = [name for name in HOOKS if (directory / name).exists() and not managed(directory / name, expected_target(repo, name))]
    if collisions:
        raise ValueError("existing hooks preserved; remove or integrate explicitly: " + ", ".join(collisions))
    current = subprocess.run(["git", "config", "--local", "--get", "alias.lore-commit"], cwd=repo, capture_output=True, text=True)
    value = current.stdout.strip()
    if current.returncode == 0 and value != ALIAS:
        raise ValueError("existing git alias preserved: lore-commit")
    if current.returncode not in {0, 1}:
        raise ValueError("cannot inspect git alias lore-commit")
    changed = []
    for name in HOOKS:
        path = directory / name
        target = expected_target(repo, name)
        if not target.is_file() or not os.access(target, os.X_OK):
            raise ValueError(f"versioned hook is absent or not executable: {target}")
        if not managed(path, target):
            path.symlink_to(target)
            changed.append(name)
    if value != ALIAS:
        subprocess.run(["git", "config", "--local", "alias.lore-commit", ALIAS], cwd=repo, check=True)
        changed.append("alias.lore-commit")
    return changed


def uninstall(repo: Path) -> list[str]:
    directory = git_dir(repo) / "hooks"
    changed = []
    for name in HOOKS:
        path = directory / name
        if managed(path, expected_target(repo, name)):
            path.unlink()
            changed.append(name)
    current = subprocess.run(["git", "config", "--local", "--get", "alias.lore-commit"], cwd=repo, capture_output=True, text=True)
    if current.returncode == 0 and current.stdout.strip() == ALIAS:
        subprocess.run(["git", "config", "--local", "--unset", "alias.lore-commit"], cwd=repo, check=True)
        changed.append("alias.lore-commit")
    return changed


def check(repo: Path) -> list[str]:
    directory = git_dir(repo) / "hooks"
    missing = [name for name in HOOKS if not managed(directory / name, expected_target(repo, name))]
    alias = subprocess.run(["git", "config", "--local", "--get", "alias.lore-commit"], cwd=repo, capture_output=True, text=True)
    if alias.returncode != 0 or alias.stdout.strip() != ALIAS:
        missing.append("alias.lore-commit")
    return missing


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--install", action="store_true")
    action.add_argument("--uninstall", action="store_true")
    action.add_argument("--check", action="store_true")
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    repo = args.repo.resolve()
    try:
        if args.install:
            print("Installed hooks: " + (", ".join(install(repo)) or "already installed"))
            return 0
        if args.uninstall:
            print("Removed hooks: " + (", ".join(uninstall(repo)) or "none"))
            return 0
        missing = check(repo)
        if missing:
            print("ERROR: hooks not installed: " + ", ".join(missing), file=sys.stderr)
            return 1
        print("Hooks and alias installed: " + ", ".join((*HOOKS, "lore-commit")))
        return 0
    except (OSError, subprocess.CalledProcessError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
