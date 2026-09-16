"""Regression tests use disposable repositories, never the published archive."""

from contextlib import redirect_stdout
import hashlib
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

from scripts.docs import promote_baseline as promoter
from scripts.docs import validate_baselines as validator


class BaselineTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="cepraea-baseline-test-")
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name)
        self.git("init", "-q")
        self.commit("empty", allow_empty=True)
        self.empty_base = self.git("rev-parse", "HEAD").strip()
        self.source_root = self.repo / ".local/drafts/arquitetura"
        self.write(".local/drafts/arquitetura/contexto/known.md", "source bytes\n")
        source = self.source_root / "contexto/known.md"
        manifest = {
            "baseline": {"id": "G0"},
            "sources": [{
                "id": "SRC-KNOWN", "path": "contexto/known.md",
                "scope": "G0 classification", "source_class": "DRAFT",
                "authority": False, "sha256": promoter.sha256(source),
            }],
        }
        self.write_yaml(".local/drafts/arquitetura/baseline/G0-SOURCES.yaml", manifest)
        self.write(".local/drafts/arquitetura/baseline/G0-EVIDENCIA.md", "# Original evidence\n")
        self.write(".local/drafts/arquitetura/baseline/G0-SHA256SUMS.txt",
                   f"{promoter.sha256(source)}  contexto/known.md\n")
        controls = []
        for logical in promoter.CONTROL_PATHS:
            control = self.write(f".local/drafts/arquitetura/{logical}", "operational control\n")
            controls.append(f"{promoter.sha256(control)}  {logical}\n")
        self.write(".local/drafts/arquitetura/baseline/G0-CONTROL-SHA256SUMS.txt", "".join(controls))
        with redirect_stdout(io.StringIO()):
            promoter.promote_g0(self.repo)
            promoter.promote_successor(self.repo, "G0-R2", "G0")
        self.commit("published G0 and R2")
        self.base = self.git("rev-parse", "HEAD").strip()

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.repo, text=True, stderr=subprocess.PIPE)

    def commit(self, message, allow_empty=False):
        self.git("add", ".")
        args = ["-c", "user.name=Baseline Test", "-c", "user.email=baseline@example.invalid",
                "commit", "-qm", message]
        if allow_empty:
            args.append("--allow-empty")
        self.git(*args)

    def write(self, relative, content):
        path = self.repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def write_yaml(self, relative, data):
        return self.write(relative, yaml.safe_dump(data, sort_keys=False))

    def registry(self):
        return yaml.safe_load((self.repo / validator.REGISTRY_PATH).read_text())

    def manifest_path(self, baseline_id):
        record = next(r for r in self.registry()["baselines"] if r["id"] == baseline_id)
        return self.repo / record["manifest"]

    def set_predecessor(self, baseline_id, predecessor):
        registry = self.registry()
        record = next(r for r in registry["baselines"] if r["id"] == baseline_id)
        record["predecessor"] = predecessor
        path = self.repo / record["manifest"]
        manifest = yaml.safe_load(path.read_text())
        manifest["baseline"]["predecessor"] = predecessor
        self.write_yaml(str(path.relative_to(self.repo)), manifest)
        self.write_yaml(validator.REGISTRY_PATH, registry)

    def promote(self, baseline_id="G0-R3", predecessor="G0-R2"):
        with redirect_stdout(io.StringIO()):
            promoter.promote_successor(self.repo, baseline_id, predecessor)

    def assert_error(self, fragment, base_ref=None):
        errors = validator.validate(self.repo, base_ref)
        self.assertTrue(any(fragment in error for error in errors), errors)

    def assert_unpublished(self, baseline_id, previous_registry):
        root = self.repo / "docs/evidence/ssot-migration/baselines"
        self.assertFalse((root / baseline_id.lower()).exists())
        self.assertEqual((self.repo / validator.REGISTRY_PATH).read_bytes(), previous_registry)
        self.assertEqual(list(root.glob(f".{baseline_id.lower()}-*")), [])

    def test_valid_chain_and_complete_root(self):
        self.assertEqual(validator.validate(self.repo, self.base), [])

    def test_initial_registry_introduction(self):
        self.assertEqual(validator.validate(self.repo, self.empty_base), [])

    def test_initial_push_sentinel(self):
        self.assertEqual(validator.validate(self.repo, "0" * 40), [])

    def test_invalid_base_ref_fails_closed(self):
        self.assert_error("cannot verify baseline immutability", "nonexistent-ref")

    def test_successor_is_allowed_without_rewriting_old_snapshots(self):
        self.promote()
        self.assertEqual(validator.validate(self.repo, self.base), [])

    def test_consistent_rewrite_is_rejected_against_base(self):
        path = self.manifest_path("G0-R2")
        manifest = yaml.safe_load(path.read_text())
        digest = hashlib.sha256(b"rewritten source").hexdigest()
        self.write(f"archive/ssot/objects/sha256/{digest}", "rewritten source")
        manifest["sources"][0]["sha256"] = digest
        self.write_yaml(str(path.relative_to(self.repo)), manifest)
        self.assertEqual(validator.validate(self.repo), [])
        self.assert_error("immutable snapshot changed", self.base)

    def test_g0_original_evidence_is_immutable(self):
        self.write("docs/evidence/ssot-migration/baselines/g0/G0-EVIDENCIA.md", "rewritten")
        self.assert_error("immutable snapshot changed", self.base)

    def test_deleted_published_record_is_rejected(self):
        registry = self.registry()
        registry["baselines"] = registry["baselines"][:1]
        self.write_yaml(validator.REGISTRY_PATH, registry)
        self.assert_error("published baseline record changed or removed", self.base)

    def test_removed_registry_is_rejected(self):
        (self.repo / validator.REGISTRY_PATH).unlink()
        errors = validator.validate_immutability(self.repo, self.base)
        self.assertIn("published baseline registry removed", errors)

    def test_immutable_flag_cannot_disable_protection(self):
        registry = self.registry()
        registry["baselines"][1]["immutable"] = False
        self.write_yaml(validator.REGISTRY_PATH, registry)
        self.assert_error("published baseline record changed", self.base)

    def test_deleted_snapshot_file_is_rejected(self):
        self.manifest_path("G0-R2").with_name("G0-R2-EVIDENCE.md").unlink()
        self.assert_error("immutable snapshot changed", self.base)

    def test_untracked_addition_to_published_snapshot_is_rejected(self):
        path = self.manifest_path("G0-R2").with_name("extra.md")
        path.write_text("new evidence")
        self.assert_error("immutable snapshot changed", self.base)

    def test_cycle_is_rejected_even_when_manifests_agree(self):
        self.promote()
        self.set_predecessor("G0-R2", "G0-R3")
        self.assert_error("cyclic baseline lineage")

    def test_self_cycle_is_rejected(self):
        self.set_predecessor("G0-R2", "G0-R2")
        self.assert_error("cyclic baseline lineage")

    def test_unknown_predecessor_is_rejected(self):
        self.set_predecessor("G0-R2", "MISSING")
        self.assert_error("unknown predecessor")

    def test_successor_without_root_is_rejected(self):
        self.set_predecessor("G0-R2", None)
        self.assert_error("lineage does not reach G0")

    def test_manifest_lineage_must_agree_with_registry(self):
        path = self.manifest_path("G0-R2")
        manifest = yaml.safe_load(path.read_text())
        manifest["baseline"]["predecessor"] = "OTHER"
        self.write_yaml(str(path.relative_to(self.repo)), manifest)
        self.assert_error("manifest predecessor differs")

    def test_metadata_is_inherited_from_registered_predecessor(self):
        path = self.manifest_path("G0-R2")
        manifest = yaml.safe_load(path.read_text())
        manifest["sources"][0]["scope"] = "R2 corrected classification"
        self.write_yaml(str(path.relative_to(self.repo)), manifest)
        self.promote()
        actual = yaml.safe_load(self.manifest_path("G0-R3").read_text())
        self.assertEqual(actual["sources"][0]["scope"], "R2 corrected classification")
        self.assertEqual(actual["sources"][0]["id"], "SRC-KNOWN")

    def test_newly_classified_source_survives_next_revision(self):
        self.write(".local/drafts/arquitetura/contexto/introduced.md", "new source")
        metadata = {"id": "SRC-INTRODUCED", "scope": "classified in R3", "authority": False}
        with patch.dict(promoter.NEW_SOURCE_METADATA, {"contexto/introduced.md": metadata}):
            self.promote()
        self.promote("G0-R4", "G0-R3")
        manifest = yaml.safe_load(self.manifest_path("G0-R4").read_text())
        introduced = next(s for s in manifest["sources"] if s["path"] == "contexto/introduced.md")
        self.assertEqual(introduced["id"], "SRC-INTRODUCED")
        self.assertEqual(introduced["scope"], "classified in R3")

    def test_promotion_does_not_depend_on_historical_draft_manifest(self):
        (self.source_root / "baseline/G0-SOURCES.yaml").unlink()
        self.promote()
        self.assertEqual(validator.validate(self.repo, self.base), [])

    def test_unknown_source_failure_is_retryable(self):
        previous = (self.repo / validator.REGISTRY_PATH).read_bytes()
        self.write(".local/drafts/arquitetura/contexto/introduced.md", "new source")
        with self.assertRaisesRegex(ValueError, "unclassified new source"):
            self.promote()
        self.assert_unpublished("G0-R3", previous)
        with patch.dict(promoter.NEW_SOURCE_METADATA, {
            "contexto/introduced.md": {"id": "SRC-INTRODUCED", "authority": False},
        }):
            self.promote()
        self.assertEqual(validator.validate(self.repo, self.base), [])

    def test_copy_failure_is_retryable(self):
        previous = (self.repo / validator.REGISTRY_PATH).read_bytes()
        with patch.object(promoter, "store_object", side_effect=OSError("copy failed")):
            with self.assertRaisesRegex(OSError, "copy failed"):
                self.promote()
        self.assert_unpublished("G0-R3", previous)
        self.promote()

    def test_late_artifact_write_failure_is_retryable(self):
        previous = (self.repo / validator.REGISTRY_PATH).read_bytes()
        write_new = promoter.write_new
        def fail_evidence(path, content):
            if path.name.endswith("-EVIDENCE.md"):
                raise OSError("evidence write failed")
            write_new(path, content)
        with patch.object(promoter, "write_new", side_effect=fail_evidence):
            with self.assertRaisesRegex(OSError, "evidence write failed"):
                self.promote()
        self.assert_unpublished("G0-R3", previous)
        self.promote()

    def test_initial_g0_copy_failure_leaves_no_publication_and_can_retry(self):
        with tempfile.TemporaryDirectory(prefix="cepraea-g0-test-") as temporary:
            repo = Path(temporary)
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            import shutil
            shutil.copytree(self.source_root, repo / ".local/drafts/arquitetura")
            with patch.object(promoter.shutil, "copyfile", side_effect=OSError("G0 copy failed")):
                with self.assertRaisesRegex(OSError, "G0 copy failed"):
                    promoter.promote_g0(repo)
            self.assertFalse((repo / "docs/evidence/ssot-migration/baselines/g0").exists())
            self.assertFalse((repo / validator.REGISTRY_PATH).exists())
            with redirect_stdout(io.StringIO()):
                promoter.promote_g0(repo)
            self.assertEqual(validator.validate(repo), [])

    def test_corrupt_existing_object_is_not_overwritten(self):
        source = self.write("new-source.md", "correct bytes")
        digest = promoter.sha256(source)
        objects = self.repo / "archive/ssot/objects/sha256"
        target = self.write(f"archive/ssot/objects/sha256/{digest}", "corrupt existing object")
        with self.assertRaisesRegex(ValueError, "immutable object corrupted"):
            promoter.store_object(source, objects)
        self.assertEqual(target.read_text(), "corrupt existing object")
        self.assertEqual(list(objects.glob(f".{digest}.*")), [])

    def test_registration_failure_rolls_back_publication_and_can_retry(self):
        previous = (self.repo / validator.REGISTRY_PATH).read_bytes()
        with patch.object(promoter.os, "replace", side_effect=OSError("registration failed")):
            with self.assertRaisesRegex(OSError, "registration failed"):
                self.promote()
        self.assert_unpublished("G0-R3", previous)
        self.assertEqual(list((self.repo / validator.REGISTRY_PATH).parent.glob(".BASELINES-*")), [])
        self.promote()
        self.assertEqual(validator.validate(self.repo, self.base), [])

    def test_existing_publication_is_never_overwritten(self):
        previous = self.manifest_path("G0-R2").read_bytes()
        with self.assertRaises(FileExistsError):
            self.promote("G0-R2", "G0")
        self.assertEqual(self.manifest_path("G0-R2").read_bytes(), previous)

    def test_unknown_predecessor_does_not_create_destination(self):
        previous = (self.repo / validator.REGISTRY_PATH).read_bytes()
        with self.assertRaisesRegex(ValueError, "registered exactly once"):
            self.promote(predecessor="MISSING")
        self.assert_unpublished("G0-R3", previous)

    def test_cli_accepts_all_revision_numbers_at_least_two(self):
        for number in (2, 9, 10, 19, 20, 100, 199):
            with self.subTest(number=number), patch.object(promoter, "promote_successor") as promote:
                with patch.object(sys, "argv", ["promote_baseline.py", f"g0-r{number}", "--repo", str(self.repo)]):
                    self.assertEqual(promoter.main(), 0)
                parent = "G0" if number == 2 else f"G0-R{number - 1}"
                promote.assert_called_once_with(self.repo, f"G0-R{number}", parent)

    def test_cli_rejects_invalid_revision_numbers(self):
        for argument in ("g0-r0", "g0-r1", "g0-r01", "g0-r-2", "g0-rfoo"):
            with self.subTest(argument=argument), patch.object(sys, "argv", ["promote_baseline.py", argument]):
                with self.assertRaises(SystemExit) as caught, patch("sys.stderr", io.StringIO()):
                    promoter.main()
                self.assertEqual(caught.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
