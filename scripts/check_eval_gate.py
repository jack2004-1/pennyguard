#!/usr/bin/env python3
"""Semantic evaluation gate (CI gate 4).

Replays the fixed offline fixture set through the rule fallback + guardrail and asserts
behavioral thresholds: zero safety escapes and relevance >= 0.90. Faithfulness is reported
but not gated at baseline (evaluation debt TD-06).

Exit 0 = pass; 1 = threshold failure.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from pennyguard.categorizer import RuleBasedCategorizer  # noqa: E402
from pennyguard.config import Config  # noqa: E402
from pennyguard.eval import Evaluator  # noqa: E402
from pennyguard.guardrail import Guardrail  # noqa: E402

MIN_RELEVANCE = 0.90


def main() -> int:
    config = Config.from_env(env={})
    report = Evaluator(RuleBasedCategorizer(), Guardrail(config)).run().as_dict()
    print(f"Eval report: {report}")

    if report["safety_escape_count"] != 0:
        print("SEMANTIC GATE FAIL: safety escapes must be zero", file=sys.stderr)
        return 1
    if report["relevance_rate"] < MIN_RELEVANCE:
        print(
            f"SEMANTIC GATE FAIL: relevance {report['relevance_rate']} < {MIN_RELEVANCE}",
            file=sys.stderr,
        )
        return 1

    print("SEMANTIC GATE PASSED: zero escapes, relevance above threshold.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
