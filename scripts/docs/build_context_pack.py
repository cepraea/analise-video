#!/usr/bin/env python3
"""Generate reproducible context excerpts; --check compares without writing."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
import tempfile
from pathlib import Path

import yaml

try:
    from .validate_routes import operational_path, validate
except ImportError:
    from validate_routes import operational_path, validate


CONFIG = "docs/context/PACKS.yaml"
ROUTES = "docs/context/ROUTES.yaml"
DECISIONS = "docs/governance/DECISIONS.yaml"
SOURCES = "docs/governance/SOURCES.yaml"
GENERATORS = ["scripts/docs/build_context_pack.py", "scripts/docs/validate_routes.py"]


def load_yaml(repo: Path, name: str, exclusions: list[str]) -> dict:
    value = yaml.safe_load(operational_path(repo, name, exclusions).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{name}: expected a YAML mapping")
    return value


def section(text: str, title: str) -> str:
    # Markdown headings in fenced examples are not section boundaries.
    headings = []
    fence = None
    offset = 0
    for line in text.splitlines(keepends=True):
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
        elif fence is None:
            match = re.match(r"^(#{1,6}) (.+?)\s*$", line)
            if match:
                heading_title = re.sub(r"[ \t]+#+$", "", match.group(2))
                headings.append((offset, len(match.group(1)), heading_title))
        offset += len(line)
    matches = [item for item in headings if item[2] == title]
    if len(matches) != 1:
        raise ValueError(f"section must occur exactly once: {title}")
    start, level, _ = matches[0]
    end = next((pos for pos, depth, _ in headings if pos > start and depth <= level), len(text))
    return text[start:end].rstrip()


def excerpt(text: str, selector: dict) -> str:
    selected = []
    for title in selector.get("sections", []):
        selected.append(section(text, title))
    table = selector.get("table")
    if table:
        block = section(text, table["section"])
        lines = [line for line in block.splitlines() if line.startswith("|")]
        if len(lines) < 2:
            raise ValueError(f"table not found: {table['section']}")
        requested = table["ids"]
        if not isinstance(requested, list) or not requested or len(set(requested)) != len(requested):
            raise ValueError("table ids must be a non-empty list of unique IDs")
        found = {identifier: [] for identifier in requested}
        for line in lines[2:]:
            identifier = line.split("|", 2)[1].strip().split()[0].strip("`")
            if identifier in found:
                found[identifier].append(line)
        for identifier, rows in found.items():
            if len(rows) != 1:
                raise ValueError(f"table ID must occur exactly once: {identifier}")
        selected.append("\n".join([f"## {table['section']}", "", *lines[:2], *[found[i][0] for i in requested]]))
    return "\n\n".join(selected) if selected else text.rstrip()


def document_closure(documents: dict, requested: list[str]) -> list[str]:
    ordered, visiting, visited = [], set(), set()

    def visit(name: str) -> None:
        if name in visiting:
            raise ValueError(f"document dependency cycle: {name}")
        if name in visited:
            return
        if name not in documents or not isinstance(documents[name], dict):
            raise ValueError(f"unknown document dependency: {name}")
        visiting.add(name)
        for dependency in documents[name].get("depends_on", []):
            visit(dependency)
        visiting.remove(name)
        visited.add(name)
        ordered.append(name)

    for name in requested:
        visit(name)
    return ordered


def indexed_records(records: list[dict], label: str) -> dict:
    result = {}
    for record in records:
        identifier = record.get("id")
        if not isinstance(identifier, str) or identifier in result:
            raise ValueError(f"{label}: missing or duplicate ID: {identifier}")
        result[identifier] = record
    return result


def fenced(text: str, language: str) -> str:
    runs = re.findall(r"`+", text)
    fence = "`" * max(3, max((len(run) + 1 for run in runs), default=3))
    return f"{fence}{language}\n{text.rstrip()}\n{fence}"


def build(repo: Path, name: str) -> str:
    # Only this known registry is read before its exclusion policy is available.
    route_path = operational_path(repo, ROUTES, ["archive/**", ".local/**"])
    errors = validate(repo, route_path)
    if errors:
        raise ValueError("; ".join(errors))
    routes = yaml.safe_load(route_path.read_text(encoding="utf-8"))
    exclusions = routes["defaults"]["exclude"]
    config = load_yaml(repo, CONFIG, exclusions)
    if config.get("schema_version") != 1:
        raise ValueError("PACKS schema_version must be 1")
    if not re.fullmatch(r"[A-Z0-9]+(?:-[A-Z0-9]+)*", name):
        raise ValueError(f"invalid pack ID: {name}")
    pack = config.get("packs", {}).get(name)
    if not isinstance(pack, dict):
        raise ValueError(f"pack is not configured: {name}")
    route_name = pack["route"]
    route = routes["routes"].get(route_name)
    if not isinstance(route, dict) or route_name == "source_audit":
        raise ValueError(f"not an operational pack route: {route_name}")

    fragments, fingerprints = [], {CONFIG, ROUTES, routes["policy"], DECISIONS, SOURCES, *GENERATORS}
    document_paths = set()
    documents = config["documents"]
    for alias in document_closure(documents, pack["documents"]):
        selector = documents[alias]
        path = selector["path"]
        if path in document_paths:
            raise ValueError(f"duplicate document path: {path}")
        document_paths.add(path)
        source = operational_path(repo, path, exclusions).read_text(encoding="utf-8")
        fragments.append((path, excerpt(source, selector)))
        fingerprints.add(path)
        for reference in selector.get("references", []):
            operational_path(repo, reference, exclusions)
            fingerprints.add(reference)

    required = set(route["required"]) | set(routes["defaults"]["always"])
    missing = sorted(required - document_paths - {DECISIONS})
    if missing:
        raise ValueError(f"required route documents absent from pack: {', '.join(missing)}")
    if routes["policy"] not in document_paths:
        raise ValueError("context policy must be included in pack")

    registry = load_yaml(repo, DECISIONS, exclusions)
    decisions = indexed_records(registry["decisions"], "decisions")
    sources = load_yaml(repo, SOURCES, exclusions)
    authority_ids = indexed_records(sources.get("authority_statements", []), "authority statements")
    selected = []
    for identifier in pack["decisions"]:
        if identifier not in decisions:
            raise ValueError(f"unknown decision: {identifier}")
        record = decisions[identifier]
        for origin in record.get("provenance", []):
            if origin["source_id"] not in authority_ids:
                raise ValueError(f"{identifier}: unknown provenance source: {origin['source_id']}")
        for affected in record.get("affected_documents", []):
            operational_path(repo, affected, exclusions)
        selected.append(record)
    if len(set(pack["decisions"])) != len(selected):
        raise ValueError("duplicate selected decision IDs")

    target = repo / "docs/context/packs" / f"{name}.md"
    lines = [
        f"# Pacote de contexto — {name}", "",
        "> Derivado gerado de fontes operacionais. Não aprova decisões nem muda estados de implementação.", "",
        f"Rota: `{route_name}`. Regenerar: `python3 scripts/docs/build_context_pack.py {name}`.", "",
        "Conferir antes de usar: `python3 scripts/docs/build_context_pack.py " + name + " --check`.", "",
        "Leia os trechos na responsabilidade de sua fonte. Links dentro dos blocos são relativos ao documento de origem.", "",
        "Se houver conflito, referência quebrada ou autoridade ausente, pare a ação dependente e registre a lacuna.", "",
        "## Fontes e integridade", "",
        "Hashes SHA-256 completos dos documentos e entradas de geração; nenhum arquivo histórico é carregado.", "",
        "| Fonte | SHA-256 |", "| --- | --- |",
    ]
    for path in sorted(fingerprints):
        source = operational_path(repo, path, exclusions)
        link = Path(os.path.relpath(source, target.parent)).as_posix()
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        lines.append(f"| [{path}]({link}) | `{digest}` |")
    for path, content in fragments:
        lines.extend(["", f"## Trecho de {path}", "", fenced(content, "markdown")])
    lines.extend([
        "", f"## Decisões de {DECISIONS}", "",
        fenced(yaml.safe_dump({"decisions": selected}, allow_unicode=True, sort_keys=False).rstrip(), "yaml"), "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pack", nargs="?")
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--check", action="store_true", help="fail on stale or edited outputs; never write")
    args = parser.parse_args()
    repo = args.repo.resolve()
    if bool(args.pack) == args.all:
        parser.error("select one pack ID or --all")
    try:
        config = load_yaml(repo, CONFIG, ["archive/**", ".local/**"])
        names = sorted(config["packs"]) if args.all else [args.pack]
        if not names:
            raise ValueError("no packs configured")
        # Validate every selected pack before writing any output.
        outputs = [
            (
                name,
                operational_path(repo, f"docs/context/packs/{name}.md", ["archive/**", ".local/**"], must_exist=False),
                build(repo, name),
            )
            for name in names
        ]
        failed = False
        for name, path, content in outputs:
            relative = f"docs/context/packs/{name}.md"
            if args.check:
                if not path.is_file() or path.read_text(encoding="utf-8") != content:
                    print(f"ERROR: stale or edited pack: {relative}; regenerate from sources", file=sys.stderr)
                    failed = True
                else:
                    print(f"Context pack valid: {relative}")
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                temporary = None
                try:
                    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as handle:
                        temporary = Path(handle.name)
                        handle.write(content)
                    temporary.replace(path)
                finally:
                    if temporary is not None:
                        temporary.unlink(missing_ok=True)
                print(f"Context pack generated: {relative} ({len(content.encode('utf-8'))} bytes)")
        return int(failed)
    except (ValueError, KeyError, TypeError, OSError, yaml.YAMLError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
