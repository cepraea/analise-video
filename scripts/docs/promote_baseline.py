#!/usr/bin/env python3
"""Publish immutable G0 and successor manifests with content-addressed objects."""

from __future__ import annotations

import argparse
import hashlib
import mimetypes
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


CONTROL_PATHS = [
    "README.md",
    "auditoria/notebooklm-contexto.md",
    "plano/PLANO-MESTRE.md",
    "plano/01-governanca-e-decisoes.md",
    "plano/02-migracao-ssot.md",
    "plano/03-contexto-minimo.md",
    "plano/04-rastreabilidade-e-validacao.md",
    "plano/05-cutover-e-operacao.md",
]
NEW_SOURCE_METADATA = {
    "contexto/generate_pdf_report.py": {
        "id": "SRC-NLM-PDF-GENERATOR",
        "source_class": "PROTOTYPE_AUTOMATION",
        "origin": "NotebookLM bundle, corrected operational prototype",
        "scope": "Deterministic PDF generation",
        "candidate_destination": None,
        "notebooklm_derived": True,
        "authority": False,
    },
    "contexto/repo_knowledge_graph.json": {
        "id": "SRC-NLM-KNOWLEDGE-GRAPH",
        "source_class": "GENERATED_DEMO",
        "origin": "Generated from repository root",
        "scope": "Repository symbol graph output",
        "candidate_destination": None,
        "notebooklm_derived": True,
        "authority": False,
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_value(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=repo, text=True).strip()


def store_object(source: Path, object_dir: Path, expected: str | None = None) -> str:
    digest = sha256(source)
    if expected is not None and digest != expected:
        raise ValueError(f"hash mismatch for {source}: expected {expected}, got {digest}")
    target = object_dir / digest
    if target.exists():
        if sha256(target) != digest:
            raise ValueError(f"immutable object corrupted: {target}")
        return digest
    temporary = object_dir / f".{digest}.new"
    shutil.copyfile(source, temporary)
    if sha256(temporary) != digest:
        raise ValueError(f"copy verification failed for {source}")
    temporary.rename(target)
    return digest


def write_new(path: Path, content: str) -> None:
    if path.exists():
        raise FileExistsError(f"published artifact already exists: {path}")
    path.write_text(content, encoding="utf-8")


def dump_yaml(data: Any) -> str:
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=100)


def update_registry(repo: Path, record: dict[str, Any]) -> None:
    path = repo / "docs/evidence/ssot-migration/BASELINES.yaml"
    if path.exists():
        registry = yaml.safe_load(path.read_text(encoding="utf-8"))
    else:
        registry = {"schema_version": 1, "decision_id": "GOV-SRC-001", "baselines": []}
    if any(item["id"] == record["id"] for item in registry["baselines"]):
        raise ValueError(f"baseline already registered: {record['id']}")
    registry["baselines"].append(record)
    path.write_text(dump_yaml(registry), encoding="utf-8")


def promote_g0(repo: Path) -> None:
    source_root = repo / ".local/drafts/arquitetura"
    old_root = source_root / "baseline"
    destination = repo / "docs/evidence/ssot-migration/baselines/g0"
    object_dir = repo / "archive/ssot/objects/sha256"
    if destination.exists():
        raise FileExistsError(f"G0 already published: {destination}")
    destination.mkdir(parents=True)
    object_dir.mkdir(parents=True, exist_ok=True)

    original_files = [
        "G0-EVIDENCIA.md",
        "G0-SOURCES.yaml",
        "G0-SHA256SUMS.txt",
        "G0-CONTROL-SHA256SUMS.txt",
    ]
    for name in original_files:
        shutil.copyfile(old_root / name, destination / name)

    manifest = yaml.safe_load((old_root / "G0-SOURCES.yaml").read_text(encoding="utf-8"))
    recovered: list[dict[str, str]] = []
    missing: list[dict[str, str]] = []
    for item in manifest["sources"]:
        candidate = source_root / item["path"]
        if candidate.exists() and sha256(candidate) == item["sha256"]:
            store_object(candidate, object_dir, item["sha256"])
            recovered.append({"path": item["path"], "sha256": item["sha256"]})
        else:
            missing.append({"path": item["path"], "sha256": item["sha256"]})

    expected_controls: dict[str, str] = {}
    for line in (old_root / "G0-CONTROL-SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        digest, logical = line.split(maxsplit=1)
        expected_controls[logical.lstrip("* ")] = digest
    for logical, digest in expected_controls.items():
        candidate = source_root / logical
        if candidate.exists() and sha256(candidate) == digest:
            store_object(candidate, object_dir, digest)
            recovered.append({"path": logical, "sha256": digest})
        else:
            missing.append({"path": logical, "sha256": digest})

    completeness = "COMPLETE" if not missing else "HASH_ONLY_PARTIAL"
    promotion = {
        "schema_version": 1,
        "baseline_id": "G0",
        "published_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "decision_ids": ["GOV-SRC-001", "GOV-SRC-002"],
        "completeness": completeness,
        "declared_items": len(recovered) + len(missing),
        "recovered_objects": len(recovered),
        "missing_historical_objects": missing,
        "note": "Original G0 files are byte-preserved; unavailable historical bytes are not reconstructed.",
    }
    write_new(destination / "PROMOTION.yaml", dump_yaml(promotion))
    update_registry(
        repo,
        {
            "id": "G0",
            "predecessor": None,
            "manifest": "docs/evidence/ssot-migration/baselines/g0/G0-SOURCES.yaml",
            "promotion": "docs/evidence/ssot-migration/baselines/g0/PROMOTION.yaml",
            "completeness": completeness,
            "immutable": True,
        },
    )
    print(f"Published G0: {completeness}; {len(recovered)} objects recovered, {len(missing)} missing")


def discover_successor_sources(
    source_root: Path, old_manifest: dict[str, Any], baseline_id: str
) -> list[dict[str, Any]]:
    previous = {item["path"]: item for item in old_manifest["sources"]}
    paths: list[str] = []
    for path in sorted(source_root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(source_root).as_posix()
        if relative.startswith(("baseline/", "plano/", "auditoria/")) or relative == "README.md":
            continue
        if "/.venv/" in f"/{relative}" or "/__pycache__/" in f"/{relative}":
            continue
        paths.append(relative)

    items: list[dict[str, Any]] = []
    for relative in paths:
        path = source_root / relative
        base = previous.get(relative) or NEW_SOURCE_METADATA.get(relative)
        if base is None:
            raise ValueError(f"unclassified new source: {relative}")
        item = dict(base)
        item.update(
            {
                "path": relative,
                "revision": baseline_id,
                "bytes": path.stat().st_size,
                "media_type": mimetypes.guess_type(path.name)[0] or "application/octet-stream",
                "sha256": sha256(path),
                "immutable": True,
            }
        )
        items.append(item)
    return items


def promote_successor(repo: Path, baseline_id: str, predecessor: str) -> None:
    source_root = repo / ".local/drafts/arquitetura"
    old_manifest_path = source_root / "baseline/G0-SOURCES.yaml"
    slug = baseline_id.lower()
    destination = repo / f"docs/evidence/ssot-migration/baselines/{slug}"
    object_dir = repo / "archive/ssot/objects/sha256"
    if destination.exists():
        raise FileExistsError(f"{baseline_id} already published: {destination}")
    destination.mkdir(parents=True)
    object_dir.mkdir(parents=True, exist_ok=True)

    old_manifest = yaml.safe_load(old_manifest_path.read_text(encoding="utf-8"))
    sources = discover_successor_sources(source_root, old_manifest, baseline_id)
    controls: list[dict[str, Any]] = []
    for relative in CONTROL_PATHS:
        path = source_root / relative
        controls.append(
            {
                "path": relative,
                "classification": "OPERATIONAL_CONTROL",
                "eligible_for_product_claims": False,
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )

    for item in sources:
        store_object(source_root / item["path"], object_dir, item["sha256"])
    for item in controls:
        store_object(source_root / item["path"], object_dir, item["sha256"])

    captured = datetime.now().astimezone().isoformat(timespec="seconds")
    manifest = {
        "schema_version": "1.0",
        "kind": "source_baseline_successor",
        "baseline": {
            "id": baseline_id,
            "predecessor": predecessor,
            "status": "CONCLUIDO",
            "completeness": "COMPLETE",
            "branch": git_value(repo, "branch", "--show-current"),
            "commit_base": git_value(repo, "rev-parse", "HEAD"),
            "captured_at": captured,
            "captured_by": "Codex",
            "approval_authority": "Davi Sermenho",
            "root": ".local/drafts/arquitetura",
            "source_count": len(sources),
            "control_artifact_count": len(controls),
        },
        "decisions": ["GOV-SRC-001", "GOV-SRC-002"],
        "rules": [
            "Inventory membership does not confer product authority.",
            "Operational controls are preserved but cannot substantiate product claims.",
            f"This revision does not overwrite {predecessor}.",
        ],
        "sources": sources,
        "controls": controls,
    }
    write_new(destination / f"{baseline_id}-SOURCES.yaml", dump_yaml(manifest))
    write_new(
        destination / f"{baseline_id}-SHA256SUMS.txt",
        "".join(f"{item['sha256']}  {item['path']}\n" for item in sources),
    )
    write_new(
        destination / f"{baseline_id}-CONTROL-SHA256SUMS.txt",
        "".join(f"{item['sha256']}  {item['path']}\n" for item in controls),
    )
    evidence = f"""# {baseline_id} — Evidência do baseline sucessor

## Controle

| Campo | Valor |
| --- | --- |
| Estado | `CONCLUÍDO` |
| Predecessor | `{predecessor}` |
| Completude | `COMPLETE` |
| Capturado em | `{captured}` |
| Fontes | {len(sources)} |
| Controles operacionais | {len(controls)} |

{baseline_id} registra o estado observado depois de {predecessor}. Ele não altera nem substitui os bytes, hashes ou limitações registrados em revisões anteriores.

Os oito controles são preservados por `GOV-SRC-002` e permanecem inelegíveis para definir o produto. Todos os {len(sources) + len(controls)} itens possuem objeto verificado no armazenamento por conteúdo.
"""
    write_new(destination / f"{baseline_id}-EVIDENCE.md", evidence)
    update_registry(
        repo,
        {
            "id": baseline_id,
            "predecessor": predecessor,
            "manifest": f"docs/evidence/ssot-migration/baselines/{slug}/{baseline_id}-SOURCES.yaml",
            "evidence": f"docs/evidence/ssot-migration/baselines/{slug}/{baseline_id}-EVIDENCE.md",
            "completeness": "COMPLETE",
            "immutable": True,
        },
    )
    print(f"Published {baseline_id}: {len(sources)} sources and {len(controls)} controls")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("baseline", help="g0 or a successor such as g0-r2")
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    if args.baseline == "g0":
        promote_g0(repo)
    else:
        match = re.fullmatch(r"g0-r([2-9][0-9]*)", args.baseline)
        if not match:
            parser.error("baseline must be g0 or g0-rN, with N >= 2")
        revision = int(match.group(1))
        baseline_id = f"G0-R{revision}"
        predecessor = "G0" if revision == 2 else f"G0-R{revision - 1}"
        promote_successor(repo, baseline_id, predecessor)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
