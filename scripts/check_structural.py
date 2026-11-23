#!/usr/bin/env python3
"""Structural / fitness checks (CI static-analysis gate, tier 1).

- The advisory categorizer package must not import the budget authority module.
- The model-facing surface must not expose budget-write, delete, shell, or exec methods.
- Every source module parses (compileall covers syntax separately in CI).

Exit 0 = pass; 1 = violation.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "pennyguard"

FORBIDDEN_NAME_PARTS = ("budget", "delete", "shell", "exec", "tool_call")


def main() -> int:
    violations: list[str] = []

    cat_dir = SRC / "categorizer"
    for py in cat_dir.glob("*.py"):
        text = py.read_text(encoding="utf-8")
        if re.search(r"from\s+\.\.?budget|import\s+budget", text):
            violations.append(f"{py.name}: categorizer must not import budget authority")
        for name in re.findall(r"def\s+([a-zA-Z_]\w*)", text):
            lowered = name.lower()
            if any(part in lowered for part in FORBIDDEN_NAME_PARTS):
                violations.append(f"{py.name}: forbidden surface method '{name}'")

    if violations:
        for v in violations:
            print(f"STRUCTURAL FAIL: {v}", file=sys.stderr)
        return 1

    print("STRUCTURAL GATE PASSED: advisory/authority boundary intact.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
