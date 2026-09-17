#!/usr/bin/env python3
"""Build or check a deterministic repository code graph for a selected Git view."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import subprocess
import sys
import tempfile
from fnmatch import fnmatchcase
from pathlib import Path, PurePosixPath

import yaml

CONFIG = "docs/context/GRAPH.yaml"
EXTRACTORS = ["scripts/context/build_code_graph.py", "scripts/context/extract_typescript_graph.mjs"]


def run(repo: Path, *args: str, check: bool = True, input_data: bytes | None = None):
    return subprocess.run(args, cwd=repo, input=input_data, capture_output=True, check=check)


def git(repo: Path, *args: str) -> bytes:
    return run(repo, "git", *args).stdout


def list_paths(repo: Path, source: str, revision: str) -> list[str]:
    if source == "workspace": raw = git(repo, "ls-files", "-co", "--exclude-standard", "-z")
    elif source == "index": raw = git(repo, "ls-files", "--cached", "-z")
    else: raw = git(repo, "ls-tree", "-r", "--name-only", "-z", revision)
    return sorted(item.decode() for item in raw.split(b"\0") if item)


def read(repo: Path, name: str, source: str, revision: str) -> bytes:
    if source == "workspace": return (repo / name).read_bytes()
    return git(repo, "show", f":{name}" if source == "index" else f"{revision}:{name}")


def revision_id(repo: Path, source: str, revision: str) -> str:
    head = git(repo, "rev-parse", revision if source == "commit" else "HEAD").decode().strip()
    return head if source == "commit" else f"{source}@{head}"


def corpus_path(name: str, config: dict) -> bool:
    if PurePosixPath(name).suffix not in set(config["extensions"]):return False
    if not any(name==root or name.startswith(root.rstrip('/')+'/') for root in config["roots"]):return False
    return not any(fnmatchcase(name,pattern) for pattern in config.get("exclude",[]))


def module_name(path: str) -> str:
    value = PurePosixPath(path)
    parts = list(value.with_suffix("").parts)
    if parts[:2] == ["backend", "src"]: parts = parts[2:]
    if parts and parts[-1] == "__init__": parts.pop()
    return ".".join(parts)


def python_extract(path: str, content: str) -> dict:
    tree = ast.parse(content, path)
    symbols=[]; imports=[]; calls=[]; scope=[]
    class Visitor(ast.NodeVisitor):
        def visit_ClassDef(self,node):
            q=".".join([*scope,node.name]); symbols.append({"name":node.name,"qualified":q,"kind":"class","line":node.lineno}); scope.append(node.name); self.generic_visit(node); scope.pop()
        def visit_FunctionDef(self,node): self.function(node,"function")
        def visit_AsyncFunctionDef(self,node): self.function(node,"async_function")
        def function(self,node,kind):
            q=".".join([*scope,node.name]); symbols.append({"name":node.name,"qualified":q,"kind":kind if not scope else "method","line":node.lineno}); scope.append(node.name); self.generic_visit(node); scope.pop()
        def visit_Import(self,node):
            for item in node.names: imports.append({"module":item.name,"bindings":[{"local":item.asname or item.name.split('.')[0],"imported":"*","kind":"namespace"}],"line":node.lineno})
        def visit_ImportFrom(self,node):
            imports.append({"module":"."*node.level+(node.module or ''),"bindings":[{"local":i.asname or i.name,"imported":i.name,"kind":"named"} for i in node.names],"line":node.lineno})
        def visit_Call(self,node):
            try: expr=ast.unparse(node.func)
            except Exception: expr="<unknown>"
            calls.append({"caller":".".join(scope) or None,"expression":expr,"line":node.lineno}); self.generic_visit(node)
    Visitor().visit(tree)
    return {"path":path,"symbols":symbols,"imports":imports,"calls":calls,"diagnostics":[]}


def resolve_relative(origin: str, spec: str, candidates: set[str]) -> str | None:
    base=PurePosixPath(origin).parent
    if spec.startswith("."):
        level=len(spec)-len(spec.lstrip('.'));parent=base
        for _ in range(max(0,level-1)):parent=parent.parent
        tail=spec[level:].lstrip("/").replace(".", "/");raw=(parent/tail).as_posix()
    else:raw=spec.replace(".", "/")
    raw=str(PurePosixPath(raw))
    for candidate in [raw, *[raw+ext for ext in (".py",".ts",".tsx",".js",".jsx")], *[raw+"/index"+ext for ext in (".ts",".tsx",".js",".jsx")], raw+"/__init__.py"]:
        if candidate in candidates:return candidate
        for prefix in ("backend/src/","frontend/src/",""):
            if prefix+candidate in candidates:return prefix+candidate
    return None


def build(repo: Path, source: str, revision: str) -> dict:
    config_bytes=read(repo,CONFIG,source,revision); config=yaml.safe_load(config_bytes)
    all_paths=list_paths(repo,source,revision)
    paths=[]
    for name in all_paths:
        if source=="workspace" and not (repo/name).is_file():continue
        if not corpus_path(name,config):continue
        paths.append(name)
    blobs={p:read(repo,p,source,revision) for p in paths}
    extracted=[python_extract(p,b.decode()) for p,b in blobs.items() if p.endswith(".py")]
    web=[{"path":p,"content":b.decode()} for p,b in blobs.items() if not p.endswith(".py")]
    ts_version=None
    if web:
        compiler=repo/"frontend/node_modules/typescript"
        if not (compiler/"package.json").is_file():raise ValueError("TypeScript compiler dependency is absent; run frontend install")
        request=json.dumps({"typescript":str(compiler),"files":web}).encode()
        if source=="workspace":
            result=run(repo,"node",str(repo/EXTRACTORS[1]),input_data=request)
        else:
            with tempfile.TemporaryDirectory(prefix="repo-code-graph-extractor-") as directory:
                helper=Path(directory)/"extract_typescript_graph.mjs";helper.write_bytes(read(repo,EXTRACTORS[1],source,revision))
                result=run(repo,"node",str(helper),input_data=request)
        parsed=json.loads(result.stdout);ts_version=parsed["typescript_version"]
        for item in parsed["files"]:
            if item["diagnostics"]:raise ValueError(f"{item['path']}: TypeScript parse diagnostics: {item['diagnostics']}")
        extracted.extend(parsed["files"])
    nodes=[];edges=[];node_ids=set();symbol_by_path={}
    def node(identifier,**data):
        if identifier in node_ids:raise ValueError(f"duplicate node ID: {identifier}")
        node_ids.add(identifier);nodes.append({"id":identifier,**data})
    def external(identifier,label,resolution):
        if identifier not in node_ids:node(identifier,type="external",name=label,resolution=resolution)
    for p in paths:
        node(f"file:{p}",type="file",path=p,module=module_name(p),sha256=hashlib.sha256(blobs[p]).hexdigest())
    for item in extracted:
        symbol_by_path[item["path"]]={"qualified":{},"top_level":{}}
        for s in item["symbols"]:
            sid=f"symbol:{item['path']}#{s['qualified']}";node(sid,type="symbol",path=item["path"],name=s["name"],qualified=s["qualified"],kind=s["kind"],line=s["line"]);symbol_by_path[item["path"]]["qualified"][s["qualified"]]=sid
            if "." not in s["qualified"]:symbol_by_path[item["path"]]["top_level"].setdefault(s["name"],sid)
            edges.append({"source":f"file:{item['path']}","target":sid,"type":"contains","method":"ast","confidence":1.0})
    candidates=set(paths)
    for item in extracted:
        imports={}
        for imp in item["imports"]:
            target=resolve_relative(item["path"],imp["module"],candidates)
            target_id=f"file:{target}" if target else f"external:module:{imp['module']}"
            if not target:external(target_id,imp["module"],"unresolved_external")
            edges.append({"source":f"file:{item['path']}","target":target_id,"type":"imports","method":"ast+module-resolution","confidence":1.0 if target else 0.5,"line":imp["line"]})
            for binding in imp["bindings"]:imports[binding["local"]]=(target,binding)
        for call in item["calls"]:
            expr=call["expression"];first=expr.split('.')[0];target=None;method="ast-lexical-name-resolution";confidence=0.8
            if "." not in expr:target=symbol_by_path[item["path"]]["top_level"].get(first)
            if not target and first in imports:
                imported_path,binding=imports[first];wanted=(expr.split('.',1)[1] if binding["kind"]=="namespace" and '.' in expr else binding["imported"])
                if imported_path:target=symbol_by_path.get(imported_path,{}).get("top_level",{}).get(wanted);method="ast-import-binding-resolution";confidence=1.0
            if not target:
                target=f"external:call:{item['path']}#{expr}";external(target,expr,"unresolved_call");method="ast-unresolved";confidence=0.0
            caller=f"file:{item['path']}"
            if call["caller"]:
                caller=next((sid for sid in node_ids if sid==f"symbol:{item['path']}#{call['caller']}"),caller)
            edges.append({"source":caller,"target":target,"type":"calls","method":method,"confidence":confidence,"line":call["line"]})
    edges=sorted(edges,key=lambda e:(e["source"],e["target"],e["type"],e.get("line",0)))
    for e in edges:
        if e["source"] not in node_ids or e["target"] not in node_ids:raise ValueError("edge endpoint absent")
    payload={"schema_version":1,"source":{"kind":source,"revision":revision_id(repo,source,revision)},"configuration":{"path":CONFIG,"sha256":hashlib.sha256(config_bytes).hexdigest()},"extractors":{"python":"python-ast-v1","javascript_typescript":"typescript-compiler-api-v1","typescript_version":ts_version,"files":{p:hashlib.sha256(read(repo,p,source,revision)).hexdigest() for p in EXTRACTORS}},"corpus":[{"path":p,"sha256":hashlib.sha256(blobs[p]).hexdigest()} for p in paths],"nodes":sorted(nodes,key=lambda n:n["id"]),"edges":edges}
    canonical=json.dumps(payload,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode();payload["graph_sha256"]=hashlib.sha256(canonical).hexdigest();return payload


def graph_hash(data: dict) -> str:
    content={key:value for key,value in data.items() if key!="graph_sha256"}
    return hashlib.sha256(json.dumps(content,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()


def check(repo: Path, source: str, revision: str) -> str:
    config=yaml.safe_load(read(repo,CONFIG,source,revision));output=config["output"]
    current=json.loads(read(repo,output,source,revision))
    if current.get("graph_sha256")!=graph_hash(current):raise ValueError(f"invalid graph_sha256 for {source}: {output}")
    expected=build(repo,source,revision)
    ignored={"source","graph_sha256"}
    current_core={key:value for key,value in current.items() if key not in ignored}
    expected_core={key:value for key,value in expected.items() if key not in ignored}
    if current_core!=expected_core:raise ValueError(f"stale code graph for {source}: {output}")
    provenance=current.get("source",{})
    if provenance.get("kind") not in {"workspace","index","commit"} or not provenance.get("revision"):
        raise ValueError(f"invalid graph source provenance: {output}")
    return output


def main()->int:
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--repo",type=Path,default=Path(__file__).resolve().parents[2]);parser.add_argument("--source",choices=["workspace","index","commit"],default="workspace");parser.add_argument("--revision",default="HEAD");parser.add_argument("--check",action="store_true");args=parser.parse_args();repo=args.repo.resolve()
    try:
        if args.check:
            output=check(repo,args.source,args.revision)
            print(f"Code graph valid for {args.source}: {output}")
        else:
            result=build(repo,args.source,args.revision);config=yaml.safe_load(read(repo,CONFIG,args.source,args.revision));output=config["output"];rendered=json.dumps(result,indent=2,ensure_ascii=False)+"\n"
            path=repo/output;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(rendered);print(f"Code graph generated: {output} ({len(result['nodes'])} nodes, {len(result['edges'])} edges)")
        return 0
    except (OSError,ValueError,KeyError,TypeError,UnicodeError,subprocess.CalledProcessError,yaml.YAMLError) as exc:print(f"ERROR: {exc}",file=sys.stderr);return 1

if __name__=="__main__":raise SystemExit(main())
