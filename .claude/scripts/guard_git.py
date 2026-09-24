"""Forces an explicit confirmation before commit, push or opening a pull request.

Usage:
  guard_git.py --hook   Claude Code PreToolUse hook (reads the tool call JSON on stdin)

CLAUDE.md says these three actions each need approval, but a memory file is context,
not configuration. A PreToolUse hook runs before any permission mode, so the prompt
appears in every session even when permissions are relaxed.
"""

import json
import re
import sys

# Matched loosely on purpose: an extra confirmation costs a keystroke, a missed one
# breaks the rule. Shell separators bound the match so only the same segment counts.
SEGMENT = r"[^;&|\n]*"
GUARDED = [
    (re.compile(rf"\bgit\b{SEGMENT}\bcommit\b"), "commit"),
    (re.compile(rf"\bgit\b{SEGMENT}\bpush\b"), "push"),
    (re.compile(rf"\bgh\s+pr{SEGMENT}\bcreate\b"), "abertura de PR"),
]
REASON = (
    "Regra inviolavel do projeto: {action} precisa de aprovacao explicita de Jorge, "
    "depois de ele validar o desenvolvimento. Aprovar uma acao nao aprova a seguinte."
)


def decide(payload):
    if payload.get("tool_name") != "Bash":
        return None
    command = payload.get("tool_input", {}).get("command", "")
    for pattern, action in GUARDED:
        if pattern.search(command):
            return action
    return None


def run_hook(stdin=None, stdout=None):
    stdin, stdout = stdin or sys.stdin, stdout or sys.stdout
    action = decide(json.load(stdin))
    if action:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": REASON.format(action=action),
        }}), file=stdout)
    return 0


if __name__ == "__main__":
    sys.exit(run_hook())
