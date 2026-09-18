"""Executable tests for scoped naming and physical-line rules."""

import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml

from scripts.docs import check_code_rules as rules


class CodeRuleTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="cepraea-code-rules-")
        self.addCleanup(temporary.cleanup)
        self.repo = Path(temporary.name)
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        (self.repo / "docs/context").mkdir(parents=True)
        self.config = self.repo / rules.CONFIG
        self.write_config()

    def write_config(self, *, size_exceptions=None, name_exceptions=None, contracts=None):
        data = {
            "schema_version": 1,
            "manual_code": {
                "extensions": [".py", ".ts", ".tsx"],
                "exclude": ["archive/**", "node_modules/**", "**/__pycache__/**"],
                "warning_lines": 300,
                "maximum_lines": 500,
                "size_exceptions": size_exceptions or [],
            },
            "naming": {
                "opaque_stems": ["utils", "helpers"],
                "path_exceptions": name_exceptions or [],
            },
            "function_prefix_contracts": contracts or [],
        }
        self.config.write_text(yaml.safe_dump(data, sort_keys=False))

    def write(self, name, text):
        path = self.repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def run_check(self, source="workspace"):
        if source == "index":
            subprocess.run(["git", "add", str(self.config.relative_to(self.repo))], cwd=self.repo, check=True)
        return rules.check(self.repo, self.config, source, "HEAD")

    def test_line_thresholds_and_explicit_exception(self):
        self.write("backend/three_hundred.py", "\n" * 300)
        self.write("backend/review_me.py", "\n" * 301)
        self.write("backend/too_large.py", "\n" * 501)
        errors, warnings = self.run_check()
        self.assertTrue(any("too_large.py: 501" in item for item in errors))
        self.assertTrue(any("review_me.py: 301" in item for item in warnings))
        self.assertFalse(any("three_hundred.py" in item for item in errors + warnings))

        exception = [{
            "path": "backend/too_large.py", "maximum_lines": 550,
            "reason": "fixture", "responsible": "test", "review_when": "next change",
        }]
        self.write_config(size_exceptions=exception)
        errors, warnings = self.run_check()
        self.assertFalse(errors)
        self.assertTrue(any("explicit exception" in item for item in warnings))
        self.write("backend/too_large.py", "\n" * 551)
        self.assertTrue(any("exceeds limit 550" in item for item in self.run_check()[0]))

    def test_naming_rules_opaque_names_and_documented_exception(self):
        self.write("backend/good_name.py", "pass\n")
        self.write("backend/BadName.py", "pass\n")
        self.write("backend/utils.py", "pass\n")
        self.write("docs/architecture/ADR-003-good-name.md", "# ADR\n")
        self.write("docs/architecture/ADR-004.md", "# ADR\n")
        errors, _ = self.run_check()
        self.assertTrue(any("BadName.py" in item for item in errors))
        self.assertTrue(any("utils.py" in item for item in errors))
        self.assertTrue(any("ADR-004.md" in item for item in errors))
        exception = [{
            "path": "docs/architecture/ADR-004.md", "reason": "fixture",
            "responsible": "test", "review_when": "rename test",
        }]
        self.write_config(name_exceptions=exception)
        errors, warnings = self.run_check()
        self.assertFalse(any("ADR-004.md" in item for item in errors))
        self.assertTrue(any("ADR-004.md" in item for item in warnings))

    def test_function_contract_reports_incompatible_prefix(self):
        self.write("backend/query_module.py", "def load_items():\n    return []\n")
        contract = [{
            "path": "backend/query_module.py", "symbol": "load_items",
            "allowed_prefixes": ["query_", "find_"], "behavior": "fixture query",
        }]
        self.write_config(contracts=contract)
        self.assertTrue(any("incompatible prefix" in item for item in self.run_check()[0]))
        self.write("backend/query_module.py", "def query_items():\n    return []\n")
        contract[0]["symbol"] = "query_items"
        self.write_config(contracts=contract)
        self.assertFalse(self.run_check()[0])

    def test_index_view_uses_staged_bytes_instead_of_workspace(self):
        self.write("backend/good_name.py", "pass\n")
        subprocess.run(["git", "add", "."], cwd=self.repo, check=True)
        self.write("backend/good_name.py", "\n" * 501)
        self.assertTrue(any("501" in item for item in self.run_check("workspace")[0]))
        self.assertFalse(self.run_check("index")[0])

    def test_exception_requires_reason_owner_and_review_condition(self):
        self.write("backend/too_large.py", "\n" * 501)
        self.write_config(size_exceptions=[{"path": "backend/too_large.py", "maximum_lines": 550}])
        self.assertTrue(any("lacks reason, responsible, review_when" in item for item in self.run_check()[0]))


if __name__ == "__main__":
    unittest.main()
