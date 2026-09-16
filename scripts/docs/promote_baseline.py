#!/usr/bin/env python3
"""Publish immutable G0 and successor manifests with content-addressed objects."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import mimetypes
import os
import re
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

if __package__:
    from .validate_baselines import (
        SOURCE_CATALOG_PATH, manifest_identity_matches, validate_catalogs, validate_lineage,
        object_directory_error, object_file_error,
    )
else:
    from validate_baselines import (
        SOURCE_CATALOG_PATH, manifest_identity_matches, validate_catalogs, validate_lineage,
        object_directory_error, object_file_error,
    )


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
    if error := object_directory_error(object_dir):
        raise ValueError(error)
    digest = sha256(source)
    if expected is not None and digest != expected:
        raise ValueError(f"hash mismatch for {source}: expected {expected}, got {digest}")
    target = object_dir / digest
    if target.exists() or target.is_symlink():
        if error := object_file_error(object_dir, digest):
            raise ValueError(error)
        if sha256(target) != digest:
            raise ValueError(f"immutable object corrupted: {target}")
        return digest
    with tempfile.NamedTemporaryFile(dir=object_dir, prefix=f".{digest}.", delete=False) as handle:
        temporary = Path(handle.name)
    try:
        shutil.copyfile(source, temporary)
        if sha256(temporary) != digest:
            raise ValueError(f"copy verification failed for {source}")
        try:
            os.link(temporary, target)  # Exclusive creation; never replace an existing object.
        except FileExistsError:
            if error := object_file_error(object_dir, digest):
                raise ValueError(error)
            if sha256(target) != digest:
                raise ValueError(f"immutable object corrupted: {target}")
    finally:
        temporary.unlink(missing_ok=True)
    return digest


def write_new(path: Path, content: str) -> None:
    with path.open("x", encoding="utf-8") as handle:
        handle.write(content)


def dump_yaml(data: Any) -> str:
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=100)


def load_registry(repo: Path) -> dict[str, Any]:
    path = repo / "docs/evidence/ssot-migration/BASELINES.yaml"
    if path.exists():
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    return {"schema_version": 1, "decision_id": "GOV-SRC-001", "baselines": []}


def update_registry(repo: Path, record: dict[str, Any]) -> None:
    """Update both catalogs under the publication lock; undo caught partial failures."""
    path = repo / "docs/evidence/ssot-migration/BASELINES.yaml"
    registry = load_registry(repo)
    if any(item["id"] == record["id"] for item in registry["baselines"]):
        raise ValueError(f"baseline already registered: {record['id']}")
    catalog_errors = validate_catalogs(repo, registry["baselines"])
    if catalog_errors:
        raise ValueError("invalid source catalog: " + "; ".join(catalog_errors))
    source_path = repo / SOURCE_CATALOG_PATH
    sources = yaml.safe_load(source_path.read_text(encoding="utf-8"))
    sources["baseline_catalogs"].append({"baseline_id": record["id"], "manifest": record["manifest"]})
    registry["baselines"].append(record)
    updates = [(path, registry), (source_path, sources)]
    staged: list[tuple[Path, Path, Path | None]] = []
    applied: list[tuple[Path, Path | None]] = []
    temporary_paths: list[Path] = []
    recovery_paths: set[Path] = set()

    def stage_bytes(target: Path, content: bytes) -> Path:
        with tempfile.NamedTemporaryFile(dir=target.parent, prefix=f".{target.stem}-", delete=False) as handle:
            temporary = Path(handle.name)
            temporary_paths.append(temporary)
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        return temporary

    try:
        for target, data in updates:
            backup = stage_bytes(target, target.read_bytes()) if target.exists() else None
            temporary = stage_bytes(target, dump_yaml(data).encode("utf-8"))
            staged.append((target, temporary, backup))
        for target, temporary, backup in staged:
            os.replace(temporary, target)
            applied.append((target, backup))
    except BaseException:
        for target, backup in reversed(applied):
            try:
                if backup is None:
                    target.unlink(missing_ok=True)
                else:
                    os.replace(backup, target)
            except OSError as exc:
                if backup is not None:
                    recovery_paths.add(backup)
                raise RuntimeError(
                    f"catalog rollback failed for {target}; recovery backup: {backup}"
                ) from exc
        raise
    finally:
        for temporary in temporary_paths:
            if temporary not in recovery_paths:
                temporary.unlink(missing_ok=True)


@contextmanager
def publication(repo: Path, destination: Path, record: dict[str, Any]):
    """Stage a publication, serialize registry updates and roll back failed registration.

    Verified content-addressed objects may remain after failure; they are safe to
    reuse on retry. Neither an old snapshot nor an old object is ever removed.
    """
    lock_path = Path(git_value(repo, "rev-parse", "--git-path", "baseline-promotion.lock"))
    if not lock_path.is_absolute():
        lock_path = repo / lock_path
    with lock_path.open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if destination.exists():
            raise FileExistsError(f"baseline already published: {destination}")
        registry = load_registry(repo)
        if any(item["id"] == record["id"] for item in registry["baselines"]):
            raise ValueError(f"baseline already registered: {record['id']}")
        catalog_errors = validate_catalogs(repo, registry["baselines"])
        if catalog_errors:
            raise ValueError("invalid source catalog: " + "; ".join(catalog_errors))
        if record["predecessor"] is not None:
            resolve_predecessor(repo, record["predecessor"])
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=destination.parent, prefix=f".{destination.name}-") as temporary:
            stage = Path(temporary) / "snapshot"
            stage.mkdir()
            yield stage
            stage.rename(destination)
            try:
                update_registry(repo, record)
            except BaseException:
                destination.rename(stage)
                raise


def resolve_predecessor(repo: Path, predecessor: str) -> dict[str, Any]:
    registry = load_registry(repo)
    lineage_errors = validate_lineage(registry["baselines"])
    ids = [item["id"] for item in registry["baselines"]]
    if len(ids) != len(set(ids)):
        lineage_errors.append("duplicate baseline IDs")
    if lineage_errors:
        raise ValueError("invalid predecessor lineage: " + "; ".join(lineage_errors))
    matches = [item for item in registry["baselines"] if item["id"] == predecessor]
    if len(matches) != 1:
        raise ValueError(f"predecessor must be registered exactly once: {predecessor}")
    record = matches[0]
    if record.get("immutable") is not True:
        raise ValueError(f"predecessor is not an immutable publication: {predecessor}")
    manifest_path = (repo / record["manifest"]).resolve()
    baseline_root = (repo / "docs/evidence/ssot-migration/baselines").resolve()
    if not manifest_path.is_relative_to(baseline_root):
        raise ValueError(f"predecessor manifest outside baseline tree: {manifest_path}")
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if not manifest_identity_matches(manifest.get("baseline", {}), predecessor):
        raise ValueError(f"predecessor manifest ID differs from registry: {predecessor}")
    if predecessor != "G0":
        for field in ("predecessor", "completeness"):
            if manifest["baseline"].get(field) != record.get(field):
                raise ValueError(f"predecessor manifest {field} differs from registry: {predecessor}")
    return manifest


def promote_g0(repo: Path) -> None:
    destination = repo / "docs/evidence/ssot-migration/baselines/g0"
    record = {
        "id": "G0",
        "predecessor": None,
        "manifest": "docs/evidence/ssot-migration/baselines/g0/G0-SOURCES.yaml",
        "promotion": "docs/evidence/ssot-migration/baselines/g0/PROMOTION.yaml",
        "immutable": True,
    }
    with publication(repo, destination, record) as stage:
        completeness, recovered, missing = prepare_g0(repo, stage)
        record["completeness"] = completeness
    print(f"Published G0: {completeness}; {recovered} objects recovered, {missing} missing")


def prepare_g0(repo: Path, destination: Path) -> tuple[str, int, int]:
    source_root = repo / ".local/drafts/arquitetura"
    old_root = source_root / "baseline"
    object_dir = repo / "archive/ssot/objects/sha256"
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
    return completeness, len(recovered), len(missing)


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
    slug = baseline_id.lower()
    destination = repo / f"docs/evidence/ssot-migration/baselines/{slug}"
    record = {
        "id": baseline_id,
        "predecessor": predecessor,
        "manifest": f"docs/evidence/ssot-migration/baselines/{slug}/{baseline_id}-SOURCES.yaml",
        "evidence": f"docs/evidence/ssot-migration/baselines/{slug}/{baseline_id}-EVIDENCE.md",
        "completeness": "COMPLETE",
        "immutable": True,
    }
    with publication(repo, destination, record) as stage:
        source_count, control_count = prepare_successor(repo, baseline_id, predecessor, stage)
    print(f"Published {baseline_id}: {source_count} sources and {control_count} controls")


def prepare_successor(repo: Path, baseline_id: str, predecessor: str, destination: Path) -> tuple[int, int]:
    source_root = repo / ".local/drafts/arquitetura"
    object_dir = repo / "archive/ssot/objects/sha256"
    object_dir.mkdir(parents=True, exist_ok=True)

    old_manifest = resolve_predecessor(repo, predecessor)
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
    return len(sources), len(controls)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("baseline", help="g0 or a successor such as g0-r2")
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    if args.baseline == "g0":
        promote_g0(repo)
    else:
        match = re.fullmatch(r"g0-r([1-9][0-9]*)", args.baseline)
        if not match or int(match.group(1)) < 2:
            parser.error("baseline must be g0 or g0-rN, with N >= 2")
        revision = int(match.group(1))
        baseline_id = f"G0-R{revision}"
        predecessor = "G0" if revision == 2 else f"G0-R{revision - 1}"
        promote_successor(repo, baseline_id, predecessor)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
