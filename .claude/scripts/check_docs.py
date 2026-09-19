"""Checks documents against docs/standards/documentation.md.

Usage:
  check_docs.py [files...]   check given files, or every doc when none is given
  check_docs.py --hook       Claude Code PostToolUse hook (reads the tool call JSON on stdin)

Rules, statuses, sizes and required sections are read from the standard and the templates,
so they stay the single source of truth.
"""

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STANDARD = Path("docs/standards/documentation.md")
TEMPLATES = Path("docs/templates")

# Catalog names in the standard mapped to type keys (also the template file names).
CATALOG_TYPES = {
    "Visão do produto": "vision",
    "ADR": "adr",
    "README": "readme",
    "Runbook": "runbook",
    "Glossário": "glossary",
}
OPTIONAL_MARK = "Só quando houver"
ADR_FILENAME = re.compile(r"^\d{4}-[a-z0-9]+(-[a-z0-9]+)*\.md$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DASHES = {"—": "travessão", "–": "meia-risca"}
NA = re.compile(r"(?<!\w)N/A(?!\w)")
INLINE_CODE = re.compile(r"`[^`]*`")


@dataclass
class Finding:
    level: str
    path: str
    line: int
    message: str

    def __str__(self):
        return f"{self.level} {self.path}:{self.line}: {self.message}"


def doc_type(path, root):
    """Returns the type key, 'generic' for other docs, or None when the file is not checked."""
    rel = path.resolve().relative_to(root.resolve())
    parts = rel.parts
    if rel.suffix != ".md":
        return None
    if rel == Path("README.md"):
        return "readme"
    if parts[0] != "docs" or parts[:2] == ("docs", "templates"):
        return None
    if parts[:2] == ("docs", "adr"):
        return "adr"
    if parts[:2] == ("docs", "runbooks"):
        return "runbook"
    if rel == Path("docs/product/vision.md"):
        return "vision"
    if rel == Path("docs/product/glossary.md"):
        return "glossary"
    return "generic"


def load_standard(root):
    lines = (root / STANDARD).read_text(encoding="utf-8").splitlines()
    _, body_start = split_frontmatter(lines)
    general = adr = None
    sizes = {}
    for line in lines[body_start:]:
        stripped = line.strip()
        if stripped.startswith("status:") and general is None:
            general = {s.strip() for s in stripped[len("status:"):].split("|")}
        elif stripped.startswith("- Status:"):
            adr = set(re.findall(r"`([^`]+)`", stripped))
        elif stripped.startswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if cells[0] in CATALOG_TYPES:
                number = re.match(r"\d+", cells[-1])
                sizes[CATALOG_TYPES[cells[0]]] = int(number.group()) if number else None
    return {"statuses": general, "adr_statuses": adr, "sizes": sizes}


def required_sections(root, kind):
    template = root / TEMPLATES / f"{kind}.md"
    if not template.exists():
        return []
    lines = template.read_text(encoding="utf-8").splitlines()
    sections = []
    for i, line in enumerate(lines):
        if not line.startswith("## "):
            continue
        body = next((l for l in lines[i + 1:] if l.strip()), "")
        if OPTIONAL_MARK not in body:
            sections.append(line[3:].strip())
    return sections


def split_frontmatter(lines):
    """Returns (fields, index of first body line) or (None, 0) when absent."""
    if not lines or lines[0].strip() != "---":
        return None, 0
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            fields = {}
            for raw in lines[1:i]:
                key, _, value = raw.partition(":")
                fields[key.strip()] = value.strip()
            return fields, i + 1
    return None, 0


def prose_lines(lines, start):
    """Yields (line number, text) outside code blocks, with inline code removed."""
    in_code = False
    for i in range(start, len(lines)):
        line = lines[i]
        if line.lstrip().startswith("```"):
            in_code = not in_code
            continue
        if not in_code:
            yield i + 1, INLINE_CODE.sub("", line)


def check_file(path, root=ROOT):
    kind = doc_type(path, root)
    if kind is None:
        return []
    rel = str(path.resolve().relative_to(root.resolve()))
    standard = load_standard(root)
    lines = path.read_text(encoding="utf-8").splitlines()
    findings = []

    def add(level, line, message):
        findings.append(Finding(level, rel, line, message))

    fields, body_start = split_frontmatter(lines)
    if kind != "readme":
        if fields is None:
            add("ERRO", 1, "frontmatter ausente (status e atualizado)")
        else:
            allowed = standard["adr_statuses"] if kind == "adr" else standard["statuses"]
            if fields.get("status") not in allowed:
                add("ERRO", 2, f"status inválido; use: {', '.join(sorted(allowed))}")
            if not DATE.match(fields.get("atualizado", "")):
                add("ERRO", 3, "atualizado ausente ou fora do formato AAAA-MM-DD")

    if kind == "adr" and not ADR_FILENAME.match(path.name):
        add("ERRO", 1, "nome do ADR deve seguir NNNN-titulo-curto.md")

    size = 0
    for number, text in prose_lines(lines, body_start):
        for char, name in DASHES.items():
            if char in text:
                add("ERRO", number, f"{name} ({char}) não é permitido; use vírgula, dois-pontos ou parênteses")
        if NA.search(text):
            add("ERRO", number, "N/A não é permitido; apague a seção que não se aplica")
        if text.strip():
            size += 1

    headings = {l[3:].strip() for l in lines if l.startswith("## ")}
    for section in required_sections(root, kind):
        if section not in headings:
            add("ERRO", 1, f"seção obrigatória ausente: ## {section}")

    limit = standard["sizes"].get(kind)
    if limit and size > limit:
        add("AVISO", 1, f"{size} linhas, referência {limit}; passar é permitido com motivo registrado")
    return findings


def all_docs(root):
    docs = sorted((root / "docs").rglob("*.md")) if (root / "docs").exists() else []
    readme = root / "README.md"
    return docs + ([readme] if readme.exists() else [])


def run_hook(root, stdin=None, stdout=None, stderr=None):
    stdin, stdout, stderr = stdin or sys.stdin, stdout or sys.stdout, stderr or sys.stderr
    payload = json.load(stdin)
    file_path = payload.get("tool_input", {}).get("file_path")
    if not file_path:
        return 0
    path = Path(file_path)
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return 0
    if not path.exists():
        return 0
    findings = check_file(path, root)
    errors = [f for f in findings if f.level == "ERRO"]
    if errors:
        # Exit 2 makes Claude Code show stderr to Claude so it fixes the document.
        print("\n".join(str(f) for f in findings), file=stderr)
        return 2
    if findings:
        context = "\n".join(str(f) for f in findings)
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": context}}), file=stdout)
    return 0


def main(argv):
    if argv[:1] == ["--hook"]:
        return run_hook(ROOT)
    paths = [Path(a) for a in argv] or all_docs(ROOT)
    findings = [f for p in paths for f in check_file(p, ROOT)]
    for finding in findings:
        print(finding)
    errors = sum(f.level == "ERRO" for f in findings)
    print(f"{len(paths)} arquivo(s), {errors} erro(s), {len(findings) - errors} aviso(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
