import io
import json
import unittest
from pathlib import Path

import check_code
import guard_git


class CheckFile(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[2]

    def write(self, name, content):
        path = self.root / "backend" / "src" / "main" / "java" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        self.addCleanup(path.unlink)
        return path

    def write_frontend(self, name, content):
        path = self.root / "frontend" / "src" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        self.addCleanup(path.unlink)
        return path

    def messages(self, path):
        return [f.message for f in check_code.check_file(path, self.root)]

    def test_accepts_clean_java(self):
        path = self.write("Clean.java", "// Keeps the port open.\nclass Clean {}\n")
        self.assertEqual(self.messages(path), [])

    def test_rejects_adr_reference(self):
        path = self.write("Ref.java", "// See ADR-0011 for the reason.\nclass Ref {}\n")
        self.assertIn("cita ADR", self.messages(path)[0])

    def test_rejects_non_ascii_in_backend(self):
        path = self.write("Acento.java", "// Configuracao padrao\nclass A {}\n".replace("padrao", "padrão"))
        self.assertIn("fora do ASCII", self.messages(path)[0])

    def test_rejects_non_ascii_in_yaml(self):
        path = self.root / "backend" / "src" / "main" / "resources" / "temp-test.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# Conexão do banco\nspring: {}\n", encoding="utf-8")
        self.addCleanup(path.unlink)
        self.assertIn("fora do ASCII", self.messages(path)[0])

    def test_allows_portuguese_text_in_frontend(self):
        path = self.write_frontend("Tela.tsx", 'export const label = "Estado do sistema: indisponível";\n')
        self.assertEqual(self.messages(path), [])

    def test_rejects_portuguese_line_comment_in_frontend(self):
        path = self.write_frontend("Tela2.tsx", '// Tradução da tela\nexport const a = 1;\n')
        self.assertIn("fora do ASCII", self.messages(path)[0])

    def test_rejects_portuguese_block_comment_in_frontend(self):
        path = self.write_frontend("Tela3.tsx", '/* Isto é um bloco\n   com acento */\nexport const a = 1;\n')
        self.assertIn("fora do ASCII", self.messages(path)[0])

    def test_ignores_file_outside_the_project(self):
        self.assertEqual(check_code.check_file(Path("/tmp/Outside.java"), self.root), [])

    def test_warns_about_a_file_nothing_references(self):
        self.write_frontend("Orphan.ts", "export const unused = 1;\n")
        messages = [f.message for f in check_code.check_unreferenced(self.root)]
        self.assertEqual(len(messages), 1)
        self.assertIn("ninguem referencia", messages[0])

    def test_does_not_warn_about_a_file_that_is_imported(self):
        self.write_frontend("Used.ts", "export const used = 1;\n")
        self.write_frontend("UsedHost.tsx", 'import { used } from "./Used";\nexport const a = used;\n')
        self.assertEqual(
            [f for f in check_code.check_unreferenced(self.root) if "Used.ts" in str(f.path)], [])

    def test_real_sources_are_clean(self):
        findings = [f for p in check_code.all_sources(self.root) for f in check_code.check_file(p, self.root)]
        self.assertEqual([str(f) for f in findings], [])


class Hook(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[2]

    def run_hook(self, payload):
        err = io.StringIO()
        code = check_code.run_hook(self.root, io.StringIO(json.dumps(payload)), io.StringIO(), err)
        return code, err.getvalue()

    def test_passes_when_there_is_no_file(self):
        self.assertEqual(self.run_hook({"tool_input": {}})[0], 0)

    def test_blocks_a_file_with_a_violation(self):
        path = self.root / "backend" / "src" / "main" / "java" / "Hooked.java"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("// ADR-0001 says so\n", encoding="utf-8")
        self.addCleanup(path.unlink)
        code, err = self.run_hook({"tool_input": {"file_path": str(path)}})
        self.assertEqual(code, 2)
        self.assertIn("cita ADR", err)


class GuardGit(unittest.TestCase):
    def decide(self, command, tool="Bash"):
        return guard_git.decide({"tool_name": tool, "tool_input": {"command": command}})

    def test_guards_commit(self):
        self.assertEqual(self.decide('git commit -m "x"'), "commit")

    def test_guards_commit_with_flags_before_the_subcommand(self):
        self.assertEqual(self.decide("git -C backend commit --amend"), "commit")

    def test_guards_push_and_pr(self):
        self.assertEqual(self.decide("git push -u origin main"), "push")
        self.assertEqual(self.decide("gh pr create --base main"), "abertura de PR")

    def test_guards_a_chained_command(self):
        self.assertEqual(self.decide("git add -A && git commit -m x"), "commit")

    def test_leaves_read_only_commands_alone(self):
        self.assertIsNone(self.decide("git status"))
        self.assertIsNone(self.decide("git log --oneline -3"))
        self.assertIsNone(self.decide("gh pr list"))

    def test_ignores_other_tools(self):
        self.assertIsNone(self.decide("git commit -m x", tool="Read"))

    def test_hook_asks_for_confirmation(self):
        out = io.StringIO()
        guard_git.run_hook(io.StringIO(json.dumps(
            {"tool_name": "Bash", "tool_input": {"command": "git push"}})), out)
        payload = json.loads(out.getvalue())["hookSpecificOutput"]
        self.assertEqual(payload["permissionDecision"], "ask")
        self.assertIn("push", payload["permissionDecisionReason"])

    def test_hook_stays_silent_for_a_safe_command(self):
        out = io.StringIO()
        guard_git.run_hook(io.StringIO(json.dumps(
            {"tool_name": "Bash", "tool_input": {"command": "git status"}})), out)
        self.assertEqual(out.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
