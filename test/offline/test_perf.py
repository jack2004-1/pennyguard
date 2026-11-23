"""Offline performance test for the categorizer + guardrail path.

Verifies: PERF-001 (offline p95 latency bound).
"""

import time
from decimal import Decimal

from pennyguard.categorizer import RuleBasedCategorizer
from pennyguard.config import Config
from pennyguard.guardrail import Guardrail
from pennyguard.models import Transaction

DESCRIPTIONS = [
    "Coffee shop", "Uber ride", "Amazon order", "Netflix subscription",
    "Rent payment", "Pharmacy", "Water bill", "Unknown hobby item",
]


def test_offline_p95_under_threshold():
    # verifies: PERF-001 — p95 per-transaction categorize+guardrail under 50 ms offline.
    config = Config.from_env(env={})
    categorizer = RuleBasedCategorizer()
    guardrail = Guardrail(config)

    latencies: list[float] = []
    for i in range(200):
        tx = Transaction(
            id=f"perf-{i}",
            description=DESCRIPTIONS[i % len(DESCRIPTIONS)],
            amount=Decimal("10"),
            date="2026-11-01",
        )
        start = time.perf_counter()
        candidate = categorizer.categorize(tx)
        guardrail.validate_candidate(candidate, tx)
        latencies.append((time.perf_counter() - start) * 1000)

    latencies.sort()
    p95 = latencies[int(0.95 * (len(latencies) - 1))]
    assert p95 < 50.0, f"p95 {p95:.2f} ms exceeds 50 ms threshold"
