"""Executable acceptance tests for the content-addressed repository code graph."""

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.context import build_code_graph as graphs
from scripts.context import build_code_graph_views as views
from scripts.context import query_code_graph as queries
from scripts.git import review_staged


ROOT = Path(__file__).resolve().parents[2]


class CodeGraphTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="cepraea-code-graph-")
        self.addCleanup(temporary.cleanup)
        self.repo = Path(temporary.name)
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        subprocess.run(
            ["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
             "commit", "--allow-empty", "-qm", "test: initialize fixture"],
            cwd=self.repo, check=True,
        )
        for name in [
            graphs.CONFIG,
            "docs/context/CODE_RULES.yaml",
            "backend/src/cepraea_video/spike_media.py",
            *graphs.EXTRACTORS,
        ]:
            target = self.repo / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        compiler = self.repo / "frontend/node_modules/typescript"
        compiler.parent.mkdir(parents=True)
        compiler.symlink_to(ROOT / "frontend/node_modules/typescript", target_is_directory=True)
        self.write("backend/src/pkg/a.py", "from .b import same as renamed\n\ndef same():\n    unknown()\n\ndef call():\n    renamed()\n")
        self.write("backend/src/pkg/b.py", "def same():\n    return 1\n")
        self.write("frontend/src/util.ts", "export function same() { return 1; }\n")
        self.write("frontend/src/main.ts", "import { same as alias } from './util';\nimport * as utils from './util';\nexport function run() { alias(); utils.same(); missing(); }\n")
        self.write("frontend/src/component.tsx", "export const Component = () => <div />;\n")
        self.write("frontend/src/legacy.js", "export function legacy() { return 1; }\n")
        self.write("frontend/src/view.jsx", "export const View = () => <span />;\n")

    def write(self, name: str, content: str) -> Path:
        target = self.repo / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        return target

    def generate(self, source: str = "workspace") -> dict:
        data = graphs.build(self.repo, source, "HEAD")
        output = self.repo / "docs/context/graph/repo-knowledge-graph.json"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        return data

    def commit(self):
        subprocess.run(["git", "add", "."], cwd=self.repo, check=True)
        subprocess.run(
            ["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
             "commit", "-qm", "test: graph fixture"],
            cwd=self.repo, check=True,
        )

    def test_python_and_typescript_ast_extractors_resolve_aliases_and_keep_unknowns(self):
        data = self.generate()
        ids = [node["id"] for node in data["nodes"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertIn("symbol:backend/src/pkg/a.py#same", ids)
        self.assertIn("symbol:backend/src/pkg/b.py#same", ids)
        for name in ("Component", "legacy", "View"):
            self.assertTrue(any(node.get("name") == name for node in data["nodes"]))
        calls = [edge for edge in data["edges"] if edge["type"] == "calls"]
        python_target = "symbol:backend/src/pkg/b.py#same"
        typescript_target = "symbol:frontend/src/util.ts#same"
        self.assertTrue(any(edge["target"] == python_target for edge in calls))
        self.assertGreaterEqual(sum(edge["target"] == typescript_target for edge in calls), 2)
        unresolved = [edge for edge in calls if edge["confidence"] == 0.0]
        self.assertTrue(unresolved)
        self.assertTrue(all(edge["method"] == "ast-unresolved" for edge in unresolved))
        node_ids = set(ids)
        self.assertTrue(all(edge["source"] in node_ids and edge["target"] in node_ids for edge in data["edges"]))
        self.assertEqual(data["extractors"]["typescript_version"], "7.0.2")

    def test_corpus_hashes_follow_rename_and_removal(self):
        before = self.generate()
        records = {item["path"]: item["sha256"] for item in before["corpus"]}
        source = self.repo / "backend/src/pkg/a.py"
        self.assertEqual(records["backend/src/pkg/a.py"], hashlib.sha256(source.read_bytes()).hexdigest())
        source.rename(self.repo / "backend/src/pkg/renamed.py")
        (self.repo / "frontend/src/legacy.js").unlink()
        after = graphs.build(self.repo, "workspace", "HEAD")
        paths = {item["path"] for item in after["corpus"]}
        self.assertIn("backend/src/pkg/renamed.py", paths)
        self.assertNotIn("backend/src/pkg/a.py", paths)
        self.assertNotIn("frontend/src/legacy.js", paths)

    def test_index_check_uses_staged_bytes_and_rejects_stale_or_tampered_graph(self):
        self.generate()
        self.commit()
        self.assertEqual(graphs.check(self.repo, "commit", "HEAD"), "docs/context/graph/repo-knowledge-graph.json")
        source = self.repo / "backend/src/pkg/a.py"
        source.write_text(source.read_text() + "\ndef workspace_only():\n    pass\n")
        self.assertEqual(graphs.check(self.repo, "index", "HEAD"), "docs/context/graph/repo-knowledge-graph.json")
        with self.assertRaisesRegex(ValueError, "stale"):
            graphs.check(self.repo, "workspace", "HEAD")
        subprocess.run(["git", "add", str(source.relative_to(self.repo))], cwd=self.repo, check=True)
        with self.assertRaisesRegex(ValueError, "stale"):
            graphs.check(self.repo, "index", "HEAD")
        self.generate("index")
        graph = self.repo / "docs/context/graph/repo-knowledge-graph.json"
        subprocess.run(["git", "add", str(graph.relative_to(self.repo))], cwd=self.repo, check=True)
        self.assertEqual(graphs.check(self.repo, "index", "HEAD"), str(graph.relative_to(self.repo)))
        changed = json.loads(graph.read_text())
        changed["corpus"][0]["sha256"] = "0" * 64
        graph.write_text(json.dumps(changed, indent=2) + "\n")
        subprocess.run(["git", "add", str(graph.relative_to(self.repo))], cwd=self.repo, check=True)
        with self.assertRaisesRegex(ValueError, "graph_sha256"):
            graphs.check(self.repo, "index", "HEAD")

    def test_query_is_bounded_and_views_share_validated_source_hash(self):
        data = self.generate()
        graph_check = subprocess.run(
            [sys.executable, str(ROOT / "scripts/context/build_code_graph.py"),
             "--repo", str(self.repo), "--check"],
            cwd=self.repo / "backend", capture_output=True, text=True,
        )
        self.assertEqual(graph_check.returncode, 0, graph_check.stderr)
        zero = queries.query(data, "frontend/src/main.ts", 0)
        one = queries.query(data, "frontend/src/main.ts", 1)
        self.assertEqual(len(zero["nodes"]), 1)
        self.assertEqual(zero["edges"], [])
        self.assertGreater(len(one["nodes"]), len(zero["nodes"]))
        rendered = views.outputs(data, self.repo / ".local/generated/context")
        digest = data["graph_sha256"]
        self.assertTrue(all(digest in content for content in rendered.values()))
        for path, content in rendered.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        graph = self.repo / "docs/context/graph/repo-knowledge-graph.json"
        command = [sys.executable, str(ROOT / "scripts/context/build_code_graph_views.py"),
                   "--repo", str(self.repo), "--check"]
        result = subprocess.run(command, cwd=self.repo / "backend", capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        invalid = json.loads(graph.read_text())
        invalid["edges"][0]["target"] = "missing:endpoint"
        invalid["graph_sha256"] = graphs.graph_hash(invalid)
        graph.write_text(json.dumps(invalid, indent=2) + "\n")
        result = subprocess.run(command, cwd=self.repo / "backend", capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("endpoint absent", result.stderr)

    def test_missing_typescript_dependency_fails_explicitly(self):
        (self.repo / "frontend/node_modules/typescript").unlink()
        with self.assertRaisesRegex(ValueError, "TypeScript compiler dependency is absent"):
            graphs.build(self.repo, "workspace", "HEAD")

    def test_staged_review_requires_graph_only_for_corpus_changes(self):
        self.generate()
        self.commit()
        documentation = self.write("docs/note.md", "Documentation only.\n")
        subprocess.run(["git", "add", str(documentation.relative_to(self.repo))], cwd=self.repo, check=True)
        self.assertFalse(any("code graph" in item for item in review_staged.review(self.repo)[0]))
        subprocess.run(["git", "reset", "-q", "HEAD", "--", str(documentation.relative_to(self.repo))], cwd=self.repo, check=True)
        source = self.repo / "backend/src/pkg/a.py"
        source.write_text(source.read_text() + "\ndef changed():\n    pass\n")
        subprocess.run(["git", "add", str(source.relative_to(self.repo))], cwd=self.repo, check=True)
        self.assertTrue(any("staged code graph invalid" in item for item in review_staged.review(self.repo)[0]))
        self.generate("index")
        graph = self.repo / "docs/context/graph/repo-knowledge-graph.json"
        subprocess.run(["git", "add", str(graph.relative_to(self.repo))], cwd=self.repo, check=True)
        self.assertFalse(any("code graph" in item for item in review_staged.review(self.repo)[0]))
        config = self.repo / graphs.CONFIG
        config.write_text(config.read_text().replace("schema_version: 1", "schema_version: 2", 1))
        subprocess.run(["git", "add", str(config.relative_to(self.repo))], cwd=self.repo, check=True)
        self.assertTrue(any("GRAPH schema_version" in item for item in review_staged.review(self.repo)[0]))


if __name__ == "__main__":
    unittest.main()
