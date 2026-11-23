#!/usr/bin/env python3
"""Test-approval gate structural check (CI gate 1).

Process gate: tests for a change are approved before implementation begins (recorded in the
review memo). This script enforces the structural counterpart: every business source module has
a paired offline test file. A source module without a test fails the gate.

Exit 0 = pass; 1 = missing pairing.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEST_DIR = ROOT / "test" / "offline"

MODULE_TO_TEST = {
    "models": "test_models",
    "rule_based": "test_categorizer",
    "llm": "test_categorizer",
    "guardrail": "test_guardrail",
    "budget": "test_budget",
    "ledger": "test_ledger",
    "eval": "test_eval",
    "prompt": "test_prompt_assembly",
    "app": "test_app_cli",
}


def main() -> int:
    test_files = {p.stem for p in TEST_DIR.glob("test_*.py")}
    missing: list[str] = []
    for module, test_stem in MODULE_TO_TEST.items():
        if test_stem not in test_files:
            missing.append(f"{module} -> {test_stem}.py")

    if missing:
        for m in missing:
            print(f"TEST-APPROVAL GATE FAIL: missing paired test for {m}", file=sys.stderr)
        return 1

    print("TEST-APPROVAL GATE PASSED: every business module has a paired offline test.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
