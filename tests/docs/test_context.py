"""Context generation tests operate on disposable copies, never on baselines."""

import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

from scripts.docs import build_context_pack as packs
from scripts.docs import validate_routes as routes


ROOT = Path(__file__).resolve().parents[2]


class ContextTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="cepraea-context-test-")
        self.addCleanup(temporary.cleanup)
        self.repo = Path(temporary.name)
        shutil.copytree(ROOT / "docs", self.repo / "docs")
        config = yaml.safe_load((ROOT / packs.CONFIG).read_text())
        references = {name for item in config["documents"].values() for name in item.get("references", [])}
        for name in ["AGENTS.md", *packs.GENERATORS, *references]:
            target = self.repo / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        self.target = self.repo / "docs/context/packs/INC-002.md"
        self.target.write_text(packs.build(self.repo, "INC-002"), encoding="utf-8")

    def change_yaml(self, relative, change):
        path = self.repo / relative
        data = yaml.safe_load(path.read_text())
        change(data)
        path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")

    def cli(self, *arguments):
        return subprocess.run(
            [sys.executable, str(ROOT / packs.GENERATORS[0]), "--repo", str(self.repo), *arguments],
            cwd=self.repo.parent, capture_output=True, text=True,
        )

    def test_deterministic_output_with_resolvable_manifest_and_full_hashes(self):
        content = packs.build(self.repo, "INC-002")
        self.assertEqual(content, packs.build(self.repo, "INC-002"))
        manifest = content.split("## Trecho de", 1)[0]
        entries = re.findall(r"\| \[([^]]+)\]\(([^)]+)\) \| `([a-f0-9]+)` \|", manifest)
        self.assertGreater(len(entries), 5)
        for name, link, digest in entries:
            self.assertEqual(len(digest), 64)
            self.assertEqual((self.target.parent / link).resolve(), self.repo / name)
            self.assertTrue((self.target.parent / link).is_file())
        self.assertNotIn(str(self.repo), content)
        self.assertEqual(self.cli("--all", "--check").returncode, 0)

    def test_source_change_fails_check_without_rewriting_then_regenerates(self):
        original = self.target.read_bytes()
        source = self.repo / "docs/SYSTEM_SPEC.md"
        source.write_text(source.read_text() + "\nNova informação de teste.\n")
        self.assertNotEqual(self.cli("INC-002", "--check").returncode, 0)
        self.assertEqual(self.target.read_bytes(), original)
        self.assertEqual(self.cli("INC-002").returncode, 0)
        self.assertNotEqual(self.target.read_bytes(), original)
        self.assertEqual(self.cli("INC-002", "--check").returncode, 0)

    def test_manual_body_edit_cannot_be_blessed_by_unchanged_hash_table(self):
        self.target.write_text(self.target.read_text() + "\nConteúdo inventado.\n")
        edited = self.target.read_bytes()
        self.assertNotEqual(self.cli("--all", "--check").returncode, 0)
        self.assertEqual(self.target.read_bytes(), edited)

    def test_missing_source_does_not_overwrite_valid_output(self):
        original = self.target.read_bytes()
        (self.repo / "docs/TRACEABILITY.md").unlink()
        result = self.cli("INC-002")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("does not exist", result.stderr)
        self.assertEqual(self.target.read_bytes(), original)

    def test_dependency_cycle_and_unknown_dependency_are_rejected(self):
        documents = {"one": {"depends_on": ["two"]}, "two": {"depends_on": ["one"]}}
        with self.assertRaisesRegex(ValueError, "cycle"):
            packs.document_closure(documents, ["one"])
        with self.assertRaisesRegex(ValueError, "unknown document"):
            packs.document_closure(documents, ["absent"])

    def test_excluded_and_symlinked_sources_are_rejected(self):
        forbidden = self.repo / ".local/drafts/source.md"
        forbidden.parent.mkdir(parents=True)
        forbidden.write_text("Não deve entrar no contexto operacional.")
        self.change_yaml(packs.CONFIG, lambda data: data["documents"]["specification"].update(path=".local/drafts/source.md"))
        with self.assertRaisesRegex(ValueError, "excluded tree"):
            packs.build(self.repo, "INC-002")
        self.change_yaml(packs.CONFIG, lambda data: data["documents"]["specification"].update(path="docs/SYSTEM_SPEC.md"))
        source = self.repo / "docs/SYSTEM_SPEC.md"
        source.unlink()
        source.symlink_to(forbidden)
        with self.assertRaisesRegex(ValueError, "symlink"):
            packs.build(self.repo, "INC-002")

    def test_required_route_coverage_is_enforced(self):
        self.change_yaml(packs.CONFIG, lambda data: data["packs"]["INC-002"]["documents"].remove("traceability"))
        with self.assertRaisesRegex(ValueError, "required route documents absent"):
            packs.build(self.repo, "INC-002")

    def test_missing_on_demand_reference_is_rejected_without_embedding_it(self):
        self.assertNotIn("# Implementar uma tarefa\n", packs.build(self.repo, "INC-002"))
        (self.repo / "skills/feature-workflow/SKILL.md").unlink()
        with self.assertRaisesRegex(ValueError, "does not exist"):
            packs.build(self.repo, "INC-002")

    def test_unknown_decision_or_provenance_source_is_rejected(self):
        self.change_yaml(packs.CONFIG, lambda data: data["packs"]["INC-002"]["decisions"].append("GOV-UNKNOWN"))
        with self.assertRaisesRegex(ValueError, "unknown decision"):
            packs.build(self.repo, "INC-002")
        self.change_yaml(packs.CONFIG, lambda data: data["packs"]["INC-002"]["decisions"].remove("GOV-UNKNOWN"))
        self.change_yaml(packs.SOURCES, lambda data: data.update(authority_statements=[]))
        with self.assertRaisesRegex(ValueError, "unknown provenance source"):
            packs.build(self.repo, "INC-002")

    def test_duplicate_decision_id_is_rejected(self):
        self.change_yaml(packs.DECISIONS, lambda data: data["decisions"].append(data["decisions"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate ID"):
            packs.build(self.repo, "INC-002")

    def test_pending_decision_is_preserved_as_data_not_promoted(self):
        content = packs.build(self.repo, "INC-002")
        decision_block = content.split(f"## Decisões de {packs.DECISIONS}\n\n", 1)[1]
        copied = yaml.safe_load(decision_block.split("\n", 1)[1].rsplit("\n", 2)[0])
        originals = yaml.safe_load((self.repo / packs.DECISIONS).read_text())["decisions"]
        indexed = {record["id"]: record for record in originals}
        for record in copied["decisions"]:
            self.assertEqual(record, indexed[record["id"]])
        pending = next(record for record in copied["decisions"] if record["id"] == "GOV-006")
        self.assertEqual(pending["status"], "PENDENTE")
        self.assertIsNone(pending["decided_at"])

    def test_missing_section_or_table_id_is_an_error(self):
        self.change_yaml(packs.CONFIG, lambda data: data["documents"]["status"].update(sections=["Ausente"]))
        with self.assertRaisesRegex(ValueError, "section must occur"):
            packs.build(self.repo, "INC-002")
        with self.assertRaisesRegex(ValueError, "table ID must occur"):
            packs.excerpt("## Dados\n\n| ID | Estado |\n| --- | --- |\n| RF-001 | PENDENTE |\n", {"table": {"section": "Dados", "ids": ["RF-002"]}})

    def test_section_extraction_ignores_fenced_headings_and_keeps_subsections(self):
        text = "# Fonte\n\n## Uma\n\n```markdown\n## Outra\n```\n\n### Detalhe\n\nFato.\n\n## Outra\n\nFim.\n"
        extracted = packs.section(text, "Uma")
        self.assertIn("### Detalhe\n\nFato.", extracted)
        self.assertNotIn("Fim.", extracted)
        self.assertEqual(packs.section(text, "Outra"), "## Outra\n\nFim.")

    def test_section_extraction_accepts_optional_closing_hashes_verbatim(self):
        text = "## Alvo ###\n\nConteúdo.\n\n## Seguinte\n\nOutro.\n"
        self.assertEqual(packs.section(text, "Alvo"), "## Alvo ###\n\nConteúdo.")

    def test_section_extraction_preserves_literal_hashes_and_rejects_normalized_duplicates(self):
        text = "## C# ###\n\nLinguagem.\n\n## Seguinte ###\n\nOutro.\n"
        self.assertEqual(packs.section(text, "C#"), "## C# ###\n\nLinguagem.")
        duplicates = "## Alvo\n\nPrimeiro.\n\n## Alvo ###\n\nSegundo.\n"
        with self.assertRaisesRegex(ValueError, "section must occur exactly once"):
            packs.section(duplicates, "Alvo")

    def test_section_extraction_ignores_closing_hash_headings_in_fences(self):
        text = "```markdown\n## Alvo ###\n```\n\n## Alvo ###\n\nConteúdo.\n"
        self.assertEqual(packs.section(text, "Alvo"), "## Alvo ###\n\nConteúdo.")

    def test_route_rejects_traversal_missing_optional_and_excluded_policy(self):
        route_path = self.repo / packs.ROUTES
        self.change_yaml(packs.ROUTES, lambda data: data["routes"]["architecture"]["required"].append("../outside.md"))
        self.assertTrue(any("relative and concrete" in error for error in routes.validate(self.repo, route_path)))
        self.change_yaml(packs.ROUTES, lambda data: data["routes"]["architecture"]["required"].remove("../outside.md"))
        (self.repo / "docs/GAME_MODEL.md").unlink()
        self.assertTrue(any("optional" in error for error in routes.validate(self.repo, route_path)))
        self.change_yaml(packs.ROUTES, lambda data: data.update(policy="archive/policy.md"))
        self.assertTrue(any("excluded tree" in error for error in routes.validate(self.repo, route_path)))

    def test_all_packs_are_validated_before_any_write(self):
        original = self.target.read_bytes()
        self.change_yaml(packs.CONFIG, lambda data: data["packs"].update({"INVALID": {"route": "absent", "documents": [], "decisions": []}}))
        result = self.cli("--all")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.target.read_bytes(), original)

    def test_later_output_symlink_does_not_allow_partial_generation(self):
        original = self.target.read_bytes()
        self.change_yaml(packs.CONFIG, lambda data: data["packs"].update({"INC-003": data["packs"]["INC-002"]}))
        (self.target.parent / "INC-003.md").symlink_to(self.target)
        result = self.cli("--all")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symlink", result.stderr)
        self.assertEqual(self.target.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
