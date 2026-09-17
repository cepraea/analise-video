"""Tests for staged review and current commit-message validation."""

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.git import review_staged
from scripts.git import install_hooks
from scripts.git import lore_commit
from scripts.git import validate_commit_message as messages


ROOT = Path(__file__).resolve().parents[2]


class GitWorkflowTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="cepraea-git-flow-")
        self.addCleanup(temporary.cleanup)
        self.repo = Path(temporary.name)
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        for name in ["docs/context/CODE_RULES.yaml", "backend/src/cepraea_video/spike_media.py"]:
            target = self.repo / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        subprocess.run(["git", "add", "."], cwd=self.repo, check=True)

    def write(self, name: str, content: str):
        path = self.repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path

    def test_index_bytes_determine_result_when_workspace_differs(self):
        path = self.write("backend/good_name.py", "value = 1\n")
        subprocess.run(["git", "add", str(path.relative_to(self.repo))], cwd=self.repo, check=True)
        path.write_text("\n" * 501)
        errors, _ = review_staged.review(self.repo)
        self.assertFalse(any("good_name.py: 501" in item for item in errors))
        subprocess.run(["git", "add", str(path.relative_to(self.repo))], cwd=self.repo, check=True)
        errors, _ = review_staged.review(self.repo)
        self.assertTrue(any("good_name.py: 501" in item for item in errors))

    def test_secret_reports_rule_without_reproducing_value(self):
        secret = "AKIA" + "1234567890ABCDEF"
        path = self.write("backend/credential.py", f'key = "{secret}"\n')
        subprocess.run(["git", "add", str(path.relative_to(self.repo))], cwd=self.repo, check=True)
        errors, _ = review_staged.review(self.repo)
        rendered = "\n".join(errors)
        self.assertIn("aws-access-key", rendered)
        self.assertNotIn(secret, rendered)

    def test_rename_delete_and_subdirectory_execution(self):
        old = self.write("backend/old_name.py", "value = 1\n")
        deleted = self.write("backend/delete_me.py", "value = 2\n")
        subprocess.run(["git", "add", str(old.relative_to(self.repo)), str(deleted.relative_to(self.repo))], cwd=self.repo, check=True)
        subprocess.run(["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "test: base\n\nTested: fixture"], cwd=self.repo, check=True)
        subprocess.run(["git", "mv", "backend/old_name.py", "backend/new_name.py"], cwd=self.repo, check=True)
        deleted.unlink()
        subprocess.run(["git", "add", "-u"], cwd=self.repo, check=True)
        self.assertFalse(review_staged.review(self.repo)[0])

    def test_commit_message_contract(self):
        valid = "fix(context): validate staged bytes\n\nTested: python3 -m unittest\nConstraint: no paid API\n"
        self.assertFalse(messages.validate(valid))
        self.assertTrue(messages.validate("fix: missing evidence\n"))
        self.assertTrue(messages.validate("bad title\n\nTested: tests\n"))
        self.assertTrue(messages.validate("fix: misplaced\n\nTested: tests\n\nbody\n"))
        self.assertTrue(messages.validate("fix: generic\n\nTested: n/a\n"))
        self.assertTrue(messages.validate("fix: unknown\n\nConfidence: high\nTested: tests\n"))

    def test_hook_install_is_reversible_and_preserves_collision(self):
        hooks = self.repo / ".githooks"
        hooks.mkdir()
        for name in install_hooks.HOOKS:
            path = hooks / name
            path.write_text("#!/bin/sh\nexit 0\n")
            path.chmod(0o755)
        self.assertEqual(set(install_hooks.install(self.repo)), {*install_hooks.HOOKS, "alias.lore-commit"})
        self.assertFalse(install_hooks.check(self.repo))
        self.assertEqual(set(install_hooks.uninstall(self.repo)), {*install_hooks.HOOKS, "alias.lore-commit"})
        existing = install_hooks.git_dir(self.repo) / "hooks/pre-commit"
        existing.write_text("#!/bin/sh\nexit 0\n")
        with self.assertRaisesRegex(ValueError, "existing hooks preserved"):
            install_hooks.install(self.repo)
        self.assertEqual(existing.read_text(), "#!/bin/sh\nexit 0\n")

    def test_lore_message_uses_only_supplied_observed_facts(self):
        class Args:
            title = "fix(context): validate index"
            tested = ["python3 -m unittest: passed"]
            not_tested = None
            constraint = ["no paid API"]
            rejected = []
        content = lore_commit.message(Args())
        self.assertFalse(messages.validate(content))
        self.assertIn("Tested: python3 -m unittest: passed", content)
        self.assertNotIn("Not-tested", content)


if __name__ == "__main__":
    unittest.main()
