import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import check_docs

REAL_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve().parent / "check_docs.py"

VALID_ADR = """---
status: aceito
atualizado: 2026-09-19
---
# ADR-0001: Usar PostgreSQL

**Decisão:** Usar PostgreSQL, porque é o padrão do time.

## Contexto
Precisamos de banco relacional.

## Alternativas descartadas
- **MySQL:** menos recursos.
- **SQLite:** não serve para produção.

## Consequências
- **Ganhos:** maturidade.
"""


class CheckDocsTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        # Uses the real standard and templates so the tests also guard their parseability.
        shutil.copytree(REAL_ROOT / "docs" / "standards", self.root / "docs" / "standards")
        shutil.copytree(REAL_ROOT / "docs" / "templates", self.root / "docs" / "templates")

    def tearDown(self):
        shutil.rmtree(self.root)

    def write(self, rel, content):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def check(self, rel, content):
        return check_docs.check_file(self.write(rel, content), self.root)

    def errors(self, findings):
        return [f for f in findings if f.level == "ERRO"]

    def warnings(self, findings):
        return [f for f in findings if f.level == "AVISO"]

    def test_valid_adr_has_no_findings(self):
        self.assertEqual(self.check("docs/adr/0001-usar-postgresql.md", VALID_ADR), [])

    def test_missing_frontmatter_is_error(self):
        content = VALID_ADR.split("---\n", 2)[2]
        errors = self.errors(self.check("docs/adr/0001-usar-postgresql.md", content))
        self.assertTrue(any("frontmatter" in f.message for f in errors))

    def test_invalid_status_for_type_is_error(self):
        content = VALID_ADR.replace("status: aceito", "status: ativo")
        errors = self.errors(self.check("docs/adr/0001-usar-postgresql.md", content))
        self.assertTrue(any("status" in f.message for f in errors))

    def test_invalid_date_is_error(self):
        content = VALID_ADR.replace("2026-09-19", "19/09/2026")
        errors = self.errors(self.check("docs/adr/0001-usar-postgresql.md", content))
        self.assertTrue(any("atualizado" in f.message for f in errors))

    def test_dashes_are_errors_with_line_number(self):
        content = VALID_ADR.replace("menos recursos.", "menos recursos — e – mais.")
        errors = self.errors(self.check("docs/adr/0001-usar-postgresql.md", content))
        self.assertEqual(len(errors), 2)
        self.assertEqual({f.line for f in errors}, {13})

    def test_dash_inside_code_is_ignored(self):
        content = VALID_ADR + "\nUse `—` assim.\n```\n—\n```\n"
        self.assertEqual(self.errors(self.check("docs/adr/0001-usar-postgresql.md", content)), [])

    def test_na_is_error(self):
        content = VALID_ADR.replace("maturidade.", "N/A")
        errors = self.errors(self.check("docs/adr/0001-usar-postgresql.md", content))
        self.assertTrue(any("N/A" in f.message for f in errors))

    def test_missing_required_section_is_error(self):
        content = VALID_ADR.replace("## Contexto", "## Cenário")
        errors = self.errors(self.check("docs/adr/0001-usar-postgresql.md", content))
        self.assertTrue(any("Contexto" in f.message for f in errors))

    def test_optional_section_may_be_absent(self):
        self.assertNotIn("Substitui", VALID_ADR)
        self.assertEqual(self.check("docs/adr/0001-usar-postgresql.md", VALID_ADR), [])

    def test_adr_filename_pattern_is_error(self):
        errors = self.errors(self.check("docs/adr/usar-postgresql.md", VALID_ADR))
        self.assertTrue(any("NNNN" in f.message for f in errors))

    def test_size_over_reference_is_only_warning(self):
        content = VALID_ADR + "".join(f"- item {i}\n" for i in range(40))
        findings = self.check("docs/adr/0001-usar-postgresql.md", content)
        self.assertEqual(self.errors(findings), [])
        self.assertEqual(len(self.warnings(findings)), 1)
        self.assertIn("referência 40", self.warnings(findings)[0].message)

    def test_code_blocks_do_not_count_for_size(self):
        content = VALID_ADR + "```\n" + "x\n" * 60 + "```\n"
        self.assertEqual(self.warnings(self.check("docs/adr/0001-usar-postgresql.md", content)), [])

    def test_readme_needs_no_frontmatter(self):
        readme = (REAL_ROOT / "docs" / "templates" / "readme.md").read_text(encoding="utf-8")
        self.assertEqual(self.errors(self.check("README.md", readme)), [])

    def test_templates_are_skipped(self):
        path = self.root / "docs" / "templates" / "adr.md"
        self.assertEqual(check_docs.check_file(path, self.root), [])

    def hook(self, rel, content):
        path = self.write(rel, content)
        stdin = io.StringIO(json.dumps({"tool_input": {"file_path": str(path)}}))
        out, err = io.StringIO(), io.StringIO()
        return check_docs.run_hook(self.root, stdin, out, err), out.getvalue(), err.getvalue()

    def test_hook_error_exits_2_with_findings_on_stderr(self):
        code, out, err = self.hook("docs/adr/0001-x.md", VALID_ADR.replace("maturidade.", "N/A"))
        self.assertEqual(code, 2)
        self.assertIn("N/A", err)

    def test_hook_warning_goes_to_additional_context(self):
        content = VALID_ADR + "".join(f"- item {i}\n" for i in range(40))
        code, out, err = self.hook("docs/adr/0001-x.md", content)
        self.assertEqual(code, 0)
        self.assertIn("referência 40", json.loads(out)["hookSpecificOutput"]["additionalContext"])

    def test_real_standard_passes(self):
        path = self.root / "docs" / "standards" / "documentation.md"
        self.assertEqual(check_docs.check_file(path, self.root), [])


class HookModeTest(unittest.TestCase):
    def run_hook(self, file_path):
        payload = json.dumps({"tool_name": "Write", "tool_input": {"file_path": str(file_path)}})
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--hook"], input=payload, capture_output=True, text=True
        )

    def test_file_outside_docs_is_ignored(self):
        result = self.run_hook(REAL_ROOT / "some" / "Code.java")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout + result.stderr, "")

    def test_valid_doc_exits_zero(self):
        result = self.run_hook(REAL_ROOT / "docs" / "standards" / "documentation.md")
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
