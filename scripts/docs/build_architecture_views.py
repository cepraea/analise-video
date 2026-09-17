#!/usr/bin/env python3
"""Validate the canonical C4 YAML model and generate deterministic Mermaid views."""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path, PurePosixPath

import yaml


MODEL = "docs/architecture/C4_MODEL.yaml"
DECISIONS = "docs/governance/DECISIONS.yaml"
ID = re.compile(r"^[a-z][a-z0-9]*(?:[.-][a-z0-9]+)*$")
TYPES = {"person", "software_system", "container", "component"}
STATES = {"implemented", "approved", "proposed"}


def indexed(items: list[dict], label: str) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for item in items:
        identifier = item.get("id") if isinstance(item, dict) else None
        if not isinstance(identifier, str) or not ID.fullmatch(identifier):
            raise ValueError(f"{label} has invalid ID: {identifier}")
        if identifier in result:
            raise ValueError(f"duplicate {label} ID: {identifier}")
        result[identifier] = item
    return result


def safe_path(name: str) -> PurePosixPath:
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts or "\\" in name:
        raise ValueError(f"invalid relative path: {name}")
    return path


def load(repo: Path, model_path: Path) -> tuple[dict, dict[str, dict], dict[str, dict]]:
    data = yaml.safe_load(model_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("C4 model schema_version must be 1")
    if data.get("status") not in {"IMPLEMENTED_NOT_VERIFIED", "VERIFIED"}:
        raise ValueError("C4 model status must use a project implementation state")
    elements = indexed(data.get("elements", []), "element")
    relationships = indexed(data.get("relationships", []), "relationship")
    decisions = yaml.safe_load((repo / DECISIONS).read_text(encoding="utf-8"))["decisions"]
    decision_index = {item["id"]: item for item in decisions}
    for decision in data.get("decisions", []):
        if decision not in decision_index or decision_index[decision]["status"] != "DECIDIDO":
            raise ValueError(f"model decision is absent or not decided: {decision}")
    for identifier, element in elements.items():
        if element.get("type") not in TYPES:
            raise ValueError(f"{identifier}: invalid element type")
        if element.get("state") not in STATES:
            raise ValueError(f"{identifier}: invalid element state")
        source = element.get("source")
        if not source or not (repo / safe_path(source)).is_file():
            raise ValueError(f"{identifier}: source does not exist: {source}")
        parent = element.get("parent")
        if element["type"] in {"container", "component"} and parent not in elements:
            raise ValueError(f"{identifier}: parent element does not exist: {parent}")
    for identifier, relation in relationships.items():
        if relation.get("source") not in elements or relation.get("target") not in elements:
            raise ValueError(f"{identifier}: relationship endpoint does not exist")
    views = indexed(data.get("views", []), "view")
    outputs: set[str] = set()
    for identifier, view in views.items():
        output = view.get("output")
        if not isinstance(output, str) or not output.startswith("docs/architecture/views/") or not output.endswith(".mmd"):
            raise ValueError(f"{identifier}: invalid view output")
        safe_path(output)
        if output in outputs:
            raise ValueError(f"duplicate view output: {output}")
        outputs.add(output)
        missing_elements = set(view.get("elements", [])) - elements.keys()
        missing_relations = set(view.get("relationships", [])) - relationships.keys()
        if missing_elements or missing_relations:
            raise ValueError(f"{identifier}: view references absent IDs")
        visible = set(view.get("elements", []))
        for relation_id in view.get("relationships", []):
            relation = relationships[relation_id]
            if relation["source"] not in visible or relation["target"] not in visible:
                raise ValueError(f"{identifier}: relationship endpoints must be visible: {relation_id}")
    return data, elements, relationships


def mermaid(view: dict, elements: dict[str, dict], relationships: dict[str, dict]) -> str:
    aliases = {identifier: f"n{index}" for index, identifier in enumerate(view["elements"], 1)}
    lines = ["flowchart LR", f"  %% Generated from {MODEL}; do not edit."]
    for identifier in view["elements"]:
        element = elements[identifier]
        label = f"{element['name']}<br/>{element.get('technology', element['type'])}"
        lines.append(f'  {aliases[identifier]}["{label}"]')
    for relation_id in view.get("relationships", []):
        relation = relationships[relation_id]
        label = relation["description"].replace('"', "'")
        lines.append(f'  {aliases[relation["source"]]} -->|"{label}"| {aliases[relation["target"]]}')
    return "\n".join(lines) + "\n"


def outputs(repo: Path, model_path: Path) -> dict[Path, str]:
    data, elements, relationships = load(repo, model_path)
    return {
        repo / safe_path(view["output"]): mermaid(view, elements, relationships)
        for view in data["views"]
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    repo = args.repo.resolve()
    try:
        generated = outputs(repo, repo / args.model)
        failed = False
        for path, content in generated.items():
            if args.check:
                if not path.is_file() or path.read_text(encoding="utf-8") != content:
                    print(f"ERROR: stale or divergent architecture view: {path.relative_to(repo)}", file=sys.stderr)
                    failed = True
                else:
                    print(f"Architecture view valid: {path.relative_to(repo)}")
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
                    temporary = Path(handle.name)
                    handle.write(content)
                temporary.replace(path)
                print(f"Architecture view generated: {path.relative_to(repo)}")
        return int(failed)
    except (KeyError, TypeError, ValueError, OSError, yaml.YAMLError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
