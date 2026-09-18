"""LFS coverage tests use real Git indexes in disposable repositories."""

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import yaml

from scripts.docs import validate_baselines as baselines
from scripts.docs import validate_lfs as validator


@unittest.skipUnless(shutil.which("git-lfs"), "Git LFS is required for integration tests")
class LFSTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="cepraea-lfs-test-")
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name)
        self.git("init", "-q")
        self.git("lfs", "install", "--local", "--skip-smudge")
        self.records = []
        self.manifests = {}
        self.write(".gitattributes", b"archive/ssot/objects/sha256/** -text -diff\n")
        self.add_baseline("G0")

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.repo, stderr=subprocess.PIPE)

    def write(self, relative, content):
        path = self.repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return path

    def write_yaml(self, relative, data):
        return self.write(relative, yaml.safe_dump(data, sort_keys=False).encode())

    def add_baseline(self, baseline_id):
        directory = f"{baselines.BASELINE_ROOT}{baseline_id.lower()}"
        record = {"id": baseline_id, "manifest": f"{directory}/{baseline_id}-SOURCES.yaml"}
        if baseline_id == "G0":
            record["promotion"] = f"{directory}/PROMOTION.yaml"
            self.write_yaml(record["promotion"], {"missing_historical_objects": []})
            self.write(f"{directory}/G0-CONTROL-SHA256SUMS.txt", b"")
        self.records.append(record)
        self.manifests[baseline_id] = {"sources": [], "controls": []}
        self.write_yaml(record["manifest"], self.manifests[baseline_id])
        self.write_yaml(baselines.REGISTRY_PATH, {"baselines": self.records})

    def add_object(self, logical, content, media=None, baseline_id="G0", category="sources"):
        digest = hashlib.sha256(content).hexdigest()
        item = {"path": logical, "sha256": digest}
        if media is not None:
            item["media_type"] = media
        manifest = self.manifests[baseline_id]
        manifest[category].append(item)
        record = next(record for record in self.records if record["id"] == baseline_id)
        self.write_yaml(record["manifest"], manifest)
        name = f"{baselines.OBJECT_ROOT}/{digest}"
        self.write(name, content)
        return name

    def track_and_stage(self, name):
        self.git("lfs", "track", "--filename", name)
        self.git("add", ".gitattributes", name)

    def assert_error(self, fragment):
        errors = validator.validate(self.repo)
        self.assertTrue(any(fragment in error for error in errors), errors)

    def test_future_untracked_binary_is_rejected_even_with_existing_lfs_objects(self):
        old = self.add_object("old.pdf", b"%PDF-1.7\nold\n", "application/pdf")
        self.track_and_stage(old)
        self.add_baseline("G0-R5")
        future = self.add_object("future.png", b"\x89PNG\r\n\x1a\nfuture", "image/png", "G0-R5")
        self.git("add", future)
        self.assert_error(f"not indexed in LFS: {future}")
        self.assertEqual(self.git("check-attr", "filter", "--", future).decode().strip().split(": ")[-1], "unspecified")
        self.track_and_stage(future)
        self.assertEqual(validator.validate(self.repo), [])

    def test_stale_index_requires_restaging_after_tracking(self):
        name = self.add_object("future.pdf", b"%PDF-1.7\nstale index\n")
        self.git("add", name)
        self.git("lfs", "track", "--filename", name)
        self.git("add", ".gitattributes")
        self.assert_error("not indexed in LFS")
        self.git("add", name)
        self.assertEqual(validator.validate(self.repo), [])

    def test_all_available_binaries_are_checked_and_text_remains_plain_git(self):
        pdf = self.add_object("original.pdf", b"%PDF-1.7\npdf\n")
        text = self.add_object("README.md", "Texto válido com acentos\n".encode(), "text/markdown")
        self.add_baseline("G0-R2")
        binary = self.add_object("control.dat", b"binary\0data", "application/octet-stream", "G0-R2", "controls")
        self.track_and_stage(pdf)
        self.track_and_stage(binary)
        self.git("add", text)
        self.assertEqual(validator.validate(self.repo), [])
        expected, errors = validator.expected_binaries(self.repo)
        self.assertEqual(errors, [])
        self.assertEqual(expected, {pdf, binary})
        self.assertNotIn(b"git-lfs.github.com/spec", self.git("show", f":{text}"))

    def test_explicit_missing_g0_object_is_preserved_as_historical_gap(self):
        available = self.add_object("available.pdf", b"%PDF-1.7\navailable\n")
        missing = self.add_object("historical.pdf", b"%PDF-1.7\nmissing\n")
        (self.repo / missing).unlink()
        self.write_yaml(self.records[0]["promotion"], {
            "missing_historical_objects": [{"sha256": Path(missing).name}],
        })
        self.track_and_stage(available)
        self.assertEqual(validator.validate(self.repo), [])

    def test_missing_undeclared_binary_is_rejected(self):
        name = self.add_object("missing.png", b"\x89PNG\r\n\x1a\nmissing")
        (self.repo / name).unlink()
        self.assert_error("object missing")

    def test_unrecovered_pointer_is_rejected(self):
        name = self.add_object("report.pdf", b"%PDF-1.7\nreport\n")
        self.track_and_stage(name)
        (self.repo / name).write_bytes(self.git("show", f":{name}"))
        self.assert_error("recovered LFS bytes differ")

    def test_recovered_bytes_are_hashed_even_when_size_matches(self):
        content = b"%PDF-1.7\nreport\n"
        name = self.add_object("report.pdf", content)
        self.track_and_stage(name)
        (self.repo / name).write_bytes(b"X" * len(content))
        self.assert_error("recovered LFS bytes differ")

    def test_lfs_oid_must_match_the_manifest_hash(self):
        name = self.add_object("report.pdf", b"%PDF-1.7\nreport\n")
        self.track_and_stage(name)
        listing = json.loads(self.git("lfs", "ls-files", "--json"))
        listing["files"][0]["oid"] = "0" * 64
        check_output = validator.subprocess.check_output
        def substitute_listing(command, **kwargs):
            if command == ["git", "lfs", "ls-files", "--json"]:
                return json.dumps(listing).encode()
            return check_output(command, **kwargs)
        with patch.object(validator.subprocess, "check_output", side_effect=substitute_listing):
            self.assert_error("LFS OID differs from baseline")

    def test_hash_named_symlink_is_rejected_even_when_bytes_match(self):
        name = self.add_object("report.pdf", b"%PDF-1.7\nreport\n")
        self.track_and_stage(name)
        external = self.write("mutable.pdf", (self.repo / name).read_bytes())
        (self.repo / name).unlink()
        (self.repo / name).symlink_to(external)
        self.assert_error("regular non-symlink")

    def test_binary_metadata_in_later_revision_overrides_text_alias(self):
        content = b"ASCII-compatible opaque binary"
        name = self.add_object("alias.txt", content, "text/plain")
        self.add_baseline("G0-R2")
        self.add_object("opaque", content, "application/x-custom-binary", "G0-R2")
        expected, errors = validator.expected_binaries(self.repo)
        self.assertEqual(errors, [])
        self.assertEqual(expected, {name})

    def test_binary_detection_checks_beyond_first_chunk(self):
        name = self.add_object("opaque", b"a" * (1024 * 1024 + 8) + b"\0")
        expected, errors = validator.expected_binaries(self.repo)
        self.assertEqual(errors, [])
        self.assertEqual(expected, {name})

    def test_utf8_chunk_boundaries_do_not_misclassify_text(self):
        name = self.add_object("text", b"a" * (1024 * 1024 - 1) + "é".encode())
        self.assertFalse(validator.is_binary({"path": "text"}, self.repo / name))

    def test_missing_git_lfs_fails_closed(self):
        self.add_object("report.pdf", b"%PDF-1.7\nreport\n")
        with patch.object(validator.subprocess, "check_output", side_effect=FileNotFoundError("git-lfs")):
            self.assert_error("cannot verify baseline LFS coverage")


if __name__ == "__main__":
    unittest.main()
