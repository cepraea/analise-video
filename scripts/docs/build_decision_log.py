#!/usr/bin/env python3
"""Build the human-readable decision log from DECISIONS.yaml."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml


def build(source: Path) -> str:
    data = yaml.safe_load(source.read_text(encoding="utf-8"))
    decisions = sorted(data.get("decisions", []), key=lambda item: item["id"])
    lines = [
        "# Registro de decisões",
        "",
        "> Visão gerada de `DECISIONS.yaml`. Nenhuma decisão exclusiva deve ser registrada aqui.",
        "",
        "| ID | Status | Data | Autoridade | Decisão |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in decisions:
        statement = " ".join(str(item["statement"]).split()).replace("|", "\\|")
        lines.append(
            f"| `{item['id']}` | `{item['status']}` | {item['decided_at']} | "
            f"{item['authority']} | {statement} |"
        )
    lines.extend(["", "Fonte canônica: [`DECISIONS.yaml`](./DECISIONS.yaml).", ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", nargs="?", default="docs/governance/DECISIONS.yaml")
    parser.add_argument("output", nargs="?", default="docs/governance/DECISION_LOG.md")
    args = parser.parse_args()
    source = Path(args.source)
    output = Path(args.output)
    output.write_text(build(source), encoding="utf-8")
    print(f"Decision log written to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
