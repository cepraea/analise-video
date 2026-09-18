#!/usr/bin/env python3
"""Generate on-demand Mermaid views tied to one validated code graph."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

try:
    from .query_code_graph import verified
except ImportError:
    from query_code_graph import verified

OUTPUT=Path(".local/generated/context")


def alias(value: str)->str:return "n"+hashlib.sha256(value.encode()).hexdigest()[:16]


def render_full(data: dict)->str:
    files={n["id"]:n for n in data["nodes"] if n["type"]=="file"};lines=["flowchart LR",f"  %% source_graph_sha256={data['graph_sha256']}"]
    for i,n in sorted(files.items()):lines.append(f'  {alias(i)}["{n["path"]}"]')
    for e in data["edges"]:
        if e["type"]=="imports" and e["source"] in files and e["target"] in files:lines.append(f"  {alias(e['source'])} --> {alias(e['target'])}")
    return "\n".join(lines)+"\n"


def group(path: str)->str:
    parts=Path(path).parts
    return "/".join(parts[:2] if parts and parts[0] in {"backend","frontend"} else parts[:1])


def render_high(data: dict)->str:
    files={n["id"]:n for n in data["nodes"] if n["type"]=="file"};groups=sorted({group(n["path"]) for n in files.values()});relations=set()
    for e in data["edges"]:
        if e["type"]=="imports" and e["source"] in files and e["target"] in files:
            a,b=group(files[e["source"]]["path"]),group(files[e["target"]]["path"])
            if a!=b:relations.add((a,b))
    lines=["flowchart LR",f"  %% source_graph_sha256={data['graph_sha256']}"]+[f'  {alias(g)}["{g}"]' for g in groups]+[f"  {alias(a)} --> {alias(b)}" for a,b in sorted(relations)]
    return "\n".join(lines)+"\n"


def outputs(data: dict, directory: Path)->dict[Path,str]:
    manifest={"schema_version":1,"source_graph_sha256":data["graph_sha256"],"views":{"full":"code-graph-full.mmd","high_level":"code-graph-high-level.mmd"}}
    return {directory/"code-graph-full.mmd":render_full(data),directory/"code-graph-high-level.mmd":render_high(data),directory/"code-graph-views.json":json.dumps(manifest,indent=2)+"\n"}


def main()->int:
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--repo",type=Path,default=Path(__file__).resolve().parents[2]);p.add_argument("--graph",default="docs/context/graph/repo-knowledge-graph.json");p.add_argument("--output",default=str(OUTPUT));p.add_argument("--check",action="store_true");args=p.parse_args();repo=args.repo.resolve()
    try:
        result=outputs(verified(repo/args.graph),repo/args.output);failed=False
        for path,content in result.items():
            if args.check:
                if not path.is_file() or path.read_text()!=content:print(f"ERROR: stale graph view: {path.relative_to(repo)}",file=sys.stderr);failed=True
            else:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(content);print(f"Graph view generated: {path.relative_to(repo)}")
        return int(failed)
    except (OSError,ValueError,KeyError,json.JSONDecodeError) as exc:print(f"ERROR: {exc}",file=sys.stderr);return 1

if __name__=="__main__":raise SystemExit(main())
