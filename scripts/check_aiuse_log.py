#!/usr/bin/env python3
"""AI-use log gate (CI gate 6).

A change touching src/ or prompts/ must also update docs/ai-use-log.yaml. If no changed
paths are supplied (e.g. a full push), the gate does not block.

Usage: python check_aiuse_log.py <changed-file> [changed-file ...]
Exit 0 = pass; 1 = code/prompt change without a log update.
"""
from __future__ import annotations

import sys


def main() -> int:
    changed = sys.argv[1:]
    if not changed:
        print("AI-USE LOG GATE: no changed paths supplied; skipping diff check.")
        return 0

    touches_code = any(p.startswith("src/") or p.startswith("prompts/") for p in changed)
    touches_log = any("docs/ai-use-log.yaml" in p for p in changed)

    if touches_code and not touches_log:
        print(
            "AI-USE LOG GATE FAIL: code/prompt changed without updating docs/ai-use-log.yaml",
            file=sys.stderr,
        )
        return 1

    print("AI-USE LOG GATE PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
