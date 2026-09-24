"""Asks for confirmation before publishing work: commit, push and opening a pull request.

Usage:
  guard_git.py --pre    Claude Code PreToolUse hook (reads the tool call JSON on stdin)
  guard_git.py --post   Claude Code PostToolUse hook, opens the approval window

CLAUDE.md says publishing needs approval, but a memory file is context, not
configuration. A PreToolUse hook runs before any permission mode, so the prompt
appears in every session even when permissions are relaxed.

The three actions almost always happen together, so the first approved one opens a
short window in which the others don't ask again. The hook never learns the answer
itself: PostToolUse only fires when the command succeeded, which means it was approved.
"""

import hashlib
import json
import re
import sys
import tempfile
import time
from pathlib import Path

WINDOW_SECONDS = 5 * 60

# Matched loosely on purpose: an extra confirmation costs a keystroke, a missed one
# breaks the rule. Shell separators bound the match so only the same segment counts.
SEGMENT = r"[^;&|\n]*"
GUARDED = [
    (re.compile(rf"\bgit\b{SEGMENT}\bcommit\b"), "commit"),
    (re.compile(rf"\bgit\b{SEGMENT}\bpush\b"), "push"),
    (re.compile(rf"\bgh\s+pr{SEGMENT}\bcreate\b"), "abertura de PR"),
]
OTHERS = {
    "commit": "push e abrir PR",
    "push": "abrir PR",
    "abertura de PR": "push",
}


def marker(session_id):
    name = hashlib.sha256((session_id or "sem-sessao").encode()).hexdigest()[:16]
    return Path(tempfile.gettempdir()) / f"claude-guard-git-{name}"


def window_is_open(session_id, now=None):
    path = marker(session_id)
    if not path.exists():
        return False
    age = (now or time.time()) - path.stat().st_mtime
    return 0 <= age < WINDOW_SECONDS


def guarded_action(payload):
    if payload.get("tool_name") != "Bash":
        return None
    command = payload.get("tool_input", {}).get("command", "")
    for pattern, action in GUARDED:
        if pattern.search(command):
            return action
    return None


def run_pre(stdin=None, stdout=None):
    stdin, stdout = stdin or sys.stdin, stdout or sys.stdout
    payload = json.load(stdin)
    action = guarded_action(payload)
    if not action or window_is_open(payload.get("session_id")):
        return 0
    minutes = WINDOW_SECONDS // 60
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "ask",
        "permissionDecisionReason":
            f"Aprovar {action}? Vale também para {OTHERS[action]} nos próximos {minutes} min.",
    }}, ensure_ascii=False), file=stdout)
    return 0


def run_post(stdin=None):
    payload = json.load(stdin or sys.stdin)
    if guarded_action(payload):
        marker(payload.get("session_id")).write_text(str(time.time()), encoding="utf-8")
    return 0


def main(argv):
    if argv[:1] == ["--post"]:
        return run_post()
    return run_pre()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
