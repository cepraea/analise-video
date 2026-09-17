"""Tests for canonical C4 YAML and derived Mermaid views."""

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

from scripts.docs import build_architecture_views as views


ROOT = Path(__file__).resolve().parents[2]


class ArchitectureViewTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="cepraea-c4-")
        self.addCleanup(temporary.cleanup)
        self.repo = Path(temporary.name)
        for name in [views.MODEL, views.DECISIONS, "docs/evidence/INC-001.md", "docs/architecture/ADR-001-primeira-implementacao.md", "frontend/package.json", "backend/pyproject.toml", "backend/src/cepraea_video/spike_storage.py", "backend/src/cepraea_video/spike_media.py"]:
            target = self.repo / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)

    def data(self):
        return yaml.safe_load((self.repo / views.MODEL).read_text())

    def save(self, data):
        (self.repo / views.MODEL).write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False))

    def cli(self, *args):
        return subprocess.run([sys.executable, str(ROOT / "scripts/docs/build_architecture_views.py"), "--repo", str(self.repo), *args], capture_output=True, text=True)

    def test_generation_is_deterministic_and_check_detects_manual_edit(self):
        self.assertEqual(self.cli().returncode, 0)
        first = {path: content for path, content in views.outputs(self.repo, self.repo / views.MODEL).items()}
        self.assertEqual(self.cli("--check").returncode, 0)
        target = next(iter(first))
        target.write_text(target.read_text() + "%% manual edit\n")
        result = self.cli("--check")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("stale or divergent", result.stderr)

    def test_duplicate_id_and_missing_endpoint_fail(self):
        data = self.data()
        data["elements"].append(dict(data["elements"][0]))
        self.save(data)
        with self.assertRaisesRegex(ValueError, "duplicate element ID"):
            views.outputs(self.repo, self.repo / views.MODEL)
        data = self.data()
        data["elements"].pop()
        data["relationships"][0]["target"] = "container.absent"
        self.save(data)
        with self.assertRaisesRegex(ValueError, "endpoint does not exist"):
            views.outputs(self.repo, self.repo / views.MODEL)

    def test_view_must_show_both_relationship_endpoints(self):
        data = self.data()
        data["views"][1]["elements"].remove("container.backend")
        self.save(data)
        with self.assertRaisesRegex(ValueError, "endpoints must be visible"):
            views.outputs(self.repo, self.repo / views.MODEL)


if __name__ == "__main__":
    unittest.main()
