#!/usr/bin/env python3
"""Return a bounded subgraph for a module, path, or symbol query."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


def verified(path: Path) -> dict:
    data=json.loads(path.read_text());digest=data.get("graph_sha256")
    content={key:value for key,value in data.items() if key!="graph_sha256"}
    actual=hashlib.sha256(json.dumps(content,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
    if digest!=actual:raise ValueError("graph_sha256 does not match graph content")
    if data.get("schema_version")!=1:raise ValueError("unsupported graph schema_version")
    nodes=data.get("nodes");edges=data.get("edges");corpus=data.get("corpus")
    if not isinstance(nodes,list) or not isinstance(edges,list) or not isinstance(corpus,list):raise ValueError("graph collections must be lists")
    ids=[node.get("id") for node in nodes]
    if any(not isinstance(identifier,str) or not identifier for identifier in ids) or len(ids)!=len(set(ids)):raise ValueError("graph node IDs must be unique non-empty strings")
    known=set(ids)
    if any(edge.get("source") not in known or edge.get("target") not in known for edge in edges):raise ValueError("graph edge endpoint absent")
    paths=[item.get("path") for item in corpus]
    if len(paths)!=len(set(paths)) or any(not re.fullmatch(r"[0-9a-f]{64}",str(item.get("sha256",""))) for item in corpus):raise ValueError("invalid corpus manifest")
    return data


def query(data: dict, term: str, depth: int=1) -> dict:
    needle=term.casefold();nodes={n["id"]:n for n in data["nodes"]}
    selected={i for i,n in nodes.items() if i.casefold()==needle}
    if not selected:selected={i for i,n in nodes.items() if n["type"]=="file" and needle in {str(n.get("path","")).casefold(),str(n.get("module","")).casefold()}}
    if not selected:selected={i for i,n in nodes.items() if n["type"]=="symbol" and needle in {str(n.get("name","")).casefold(),str(n.get("qualified","")).casefold()}}
    if not selected:selected={i for i,n in nodes.items() if needle in " ".join(str(n.get(k,"")) for k in ("id","path","module","name","qualified")).casefold()}
    if not selected:raise ValueError(f"no graph node matches: {term}")
    for _ in range(depth):
        edges=[e for e in data["edges"] if e["source"] in selected or e["target"] in selected]
        expanded=selected|{e["source"] for e in edges}|{e["target"] for e in edges}
        if expanded==selected:break
        selected=expanded
    return {"schema_version":1,"query":term,"depth":depth,"source_graph_sha256":data["graph_sha256"],"nodes":[nodes[i] for i in sorted(selected)],"edges":[e for e in data["edges"] if e["source"] in selected and e["target"] in selected]}


def main()->int:
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("query");p.add_argument("--graph",type=Path,default=Path("docs/context/graph/repo-knowledge-graph.json"));p.add_argument("--depth",type=int,default=1);args=p.parse_args()
    try:
        if args.depth not in range(0,4):raise ValueError("depth must be between 0 and 3")
        print(json.dumps(query(verified(args.graph),args.query,args.depth),indent=2,ensure_ascii=False));return 0
    except (OSError,ValueError,KeyError,json.JSONDecodeError) as exc:print(f"ERROR: {exc}",file=sys.stderr);return 1

if __name__=="__main__":raise SystemExit(main())
