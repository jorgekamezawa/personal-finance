"""Blocks a commit whose Java files are not formatted.

Usage:
  guard_format.py --pre   Claude Code PreToolUse hook (reads the tool call JSON on stdin)

The formatter is a machine decision, so the commit is denied instead of asked:
running one command fixes it. The check is skipped when no Java file is staged,
which keeps a documentation commit free of it.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"

SEGMENT = r"[^;&|\n]*"
COMMIT = re.compile(rf"\bgit\b{SEGMENT}\bcommit\b")


def is_commit(payload):
    if payload.get("tool_name") != "Bash":
        return False
    return bool(COMMIT.search(payload.get("tool_input", {}).get("command", "")))


def staged_java_files():
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        cwd=ROOT, capture_output=True, text=True, check=False)
    return [line for line in result.stdout.splitlines() if line.endswith(".java")]


def format_is_clean():
    result = subprocess.run(
        ["./gradlew", "spotlessCheck", "-q"],
        cwd=BACKEND, capture_output=True, text=True, check=False)
    return result.returncode == 0


def deny(reason, stdout):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}, ensure_ascii=False), file=stdout)


def run_pre(stdin=None, stdout=None):
    stdin, stdout = stdin or sys.stdin, stdout or sys.stdout
    payload = json.load(stdin)
    if not is_commit(payload) or not staged_java_files():
        return 0
    if format_is_clean():
        return 0
    deny("Arquivo Java fora do formato. Rode ./gradlew spotlessApply no backend e comite de novo.", stdout)
    return 0


if __name__ == "__main__":
    sys.exit(run_pre())
