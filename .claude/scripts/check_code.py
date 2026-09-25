"""Checks source files against the conventions in .claude/rules/.

Usage:
  check_code.py [files...]   check given files, or every source file when none is given
  check_code.py --hook       Claude Code PostToolUse hook (reads the tool call JSON on stdin)

Only mechanical rules live here. Judgement (is this comment worth keeping, is this
name right) belongs to the review, not to a script.
"""

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Backend and operations files carry no user-facing text, so any accented character
# there is a comment or an identifier that breaks on a machine with another encoding.
ASCII_ONLY_SUFFIXES = {".java", ".kts", ".gradle", ".yaml", ".yml", ".sql", ".properties"}
ASCII_ONLY_NAMES = {"Dockerfile", "Caddyfile"}
# Frontend files show Portuguese text, so only their comments must stay ASCII.
COMMENT_ONLY_SUFFIXES = {".ts", ".tsx", ".js", ".jsx", ".css"}

SOURCE_DIRS = ("backend/src", "frontend/src", "frontend/public", ".github/workflows")
EXTRA_FILES = (
    "docker-compose.yml",
    "backend/build.gradle.kts",
    "backend/settings.gradle.kts",
    "backend/Dockerfile",
    "frontend/Dockerfile",
    "frontend/Caddyfile",
)
SKIP_DIRS = {"node_modules", "build", "dist", "bin", ".gradle", "__pycache__"}

ADR_REFERENCE = re.compile(r"\bADR-\d{4}\b")
NON_ASCII = re.compile(r"[^\x00-\x7F]")
LINE_COMMENT = re.compile(r"//(.*)$")
# Files nothing imports by name: entry points and files a config or a glob picks up.
ENTRY_POINTS = {"main.tsx", "setupTests.ts", "vite-env.d.ts"}


@dataclass
class Finding:
    level: str
    path: Path
    line: int
    message: str

    def __str__(self):
        return f"{self.level} {self.path}:{self.line} {self.message}"


def is_ascii_only(path):
    return path.suffix in ASCII_ONLY_SUFFIXES or path.name in ASCII_ONLY_NAMES


def is_source(path):
    return is_ascii_only(path) or path.suffix in COMMENT_ONLY_SUFFIXES


def comment_ranges(lines):
    """Yields (line number, comment text) for every comment in a C-style source file."""
    in_block = False
    for number, line in enumerate(lines, 1):
        rest = line
        if in_block:
            end = rest.find("*/")
            if end < 0:
                yield number, rest
                continue
            yield number, rest[:end]
            rest, in_block = rest[end + 2:], False
        while True:
            block = rest.find("/*")
            inline = LINE_COMMENT.search(rest)
            if inline and (block < 0 or inline.start() < block):
                yield number, inline.group(1)
                break
            if block < 0:
                break
            end = rest.find("*/", block + 2)
            if end < 0:
                yield number, rest[block + 2:]
                in_block = True
                break
            yield number, rest[block + 2:end]
            rest = rest[end + 2:]


def check_file(path, root):
    if not path.exists() or not is_source(path):
        return []
    try:
        relative = path.resolve().relative_to(root.resolve())
    except ValueError:
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    findings = []

    for number, line in enumerate(lines, 1):
        if ADR_REFERENCE.search(line):
            findings.append(Finding("ERRO", relative, number,
                "cita ADR no código: a decisão vive no ADR e a referência apodrece quando ele é substituído"))

    if is_ascii_only(path):
        for number, line in enumerate(lines, 1):
            found = NON_ASCII.findall(line)
            if found:
                findings.append(Finding("ERRO", relative, number,
                    f"caractere fora do ASCII ({''.join(sorted(set(found)))}): o build quebra em máquina com outra codificação"))
    else:
        for number, comment in comment_ranges(lines):
            found = NON_ASCII.findall(comment)
            if found:
                findings.append(Finding("ERRO", relative, number,
                    f"comentário com caractere fora do ASCII ({''.join(sorted(set(found)))}): comentário fica em inglês"))

    return findings


def all_sources(root):
    paths = []
    for directory in SOURCE_DIRS:
        base = root / directory
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if path.is_file() and not SKIP_DIRS & set(path.parts) and is_source(path):
                paths.append(path)
    paths += [root / name for name in EXTRA_FILES if (root / name).exists()]
    return paths


def check_unreferenced(root):
    """Warns about files under frontend/src and frontend/public that nothing mentions."""
    base = root / "frontend"
    if not base.exists():
        return []
    haystack = []
    for path in base.rglob("*"):
        if path.is_file() and not SKIP_DIRS & set(path.parts) and path.suffix in {
            ".ts", ".tsx", ".js", ".jsx", ".css", ".html", ".json", ".webmanifest",
        }:
            haystack.append((path, path.read_text(encoding="utf-8", errors="ignore")))

    findings = []
    for directory in ("src", "public"):
        for path in sorted((base / directory).rglob("*")):
            if not path.is_file() or SKIP_DIRS & set(path.parts):
                continue
            if path.name in ENTRY_POINTS or ".test." in path.name:
                continue
            stem = path.stem if path.suffix in {".ts", ".tsx", ".js", ".jsx"} else path.name
            if any(other != path and stem in text for other, text in haystack):
                continue
            findings.append(Finding("AVISO", path.relative_to(root), 0,
                "ninguém referencia este arquivo: sobra de andaime ou código morto"))
    return findings


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
    findings = check_file(path, root)
    if findings:
        # Exit 2 makes Claude Code show stderr to Claude so it fixes the file.
        print("\n".join(str(f) for f in findings), file=stderr)
        return 2
    return 0


def main(argv):
    if argv[:1] == ["--hook"]:
        return run_hook(ROOT)
    paths = [Path(a) for a in argv]
    findings = [f for p in (paths or all_sources(ROOT)) for f in check_file(p, ROOT)]
    if not paths:
        findings += check_unreferenced(ROOT)
    for finding in findings:
        print(finding)
    errors = sum(f.level == "ERRO" for f in findings)
    total = len(paths or all_sources(ROOT))
    print(f"{total} arquivo(s), {errors} erro(s), {len(findings) - errors} aviso(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
