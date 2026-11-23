"""Offline tests for deterministic budget policy.

Verifies: FR-004, INV-003.
"""

from decimal import Decimal

from pennyguard.budget import BudgetPolicy
from pennyguard.models import (
    BudgetStatus,
    CategorizationResult,
    GuardrailDecision,
    STATUS_OVER,
    STATUS_WITHIN,
)


def _record(tx_id: str, category: str, amount: str) -> CategorizationResult:
    return CategorizationResult(
        transaction_id=tx_id,
        description="item",
        amount=Decimal(amount),
        category=category,
        source="rule",
        guardrail=GuardrailDecision(accepted=True, category=category, reason_code="OK"),
    )


def test_over_budget_flag_exact():
    # verifies: FR-004 — exact decimal accumulation and over/under flag.
    policy = BudgetPolicy({"food": Decimal("100"), "transport": Decimal("200")})
    records = [
        _record("r1", "food", "60"),
        _record("r2", "food", "60"),
        _record("r3", "transport", "50"),
    ]
    statuses = {s.category: s for s in policy.evaluate(records)}
    assert statuses["food"].status == STATUS_OVER
    assert statuses["food"].spent == Decimal("120")
    assert statuses["transport"].status == STATUS_WITHIN


def test_ai_cannot_flip_compliance():
    # verifies: INV-003 — compliance comes only from policy; no model signal can flip it.
    policy = BudgetPolicy({"food": Decimal("100")})
    records = [_record("r1", "food", "120")]
    statuses = policy.evaluate(records)
    food = next(s for s in statuses if s.category == "food")
    # Even though an advisory layer might claim "compliant", policy still computes over.
    assert food.status == STATUS_OVER
    # Policy evaluate accepts only persisted records; no model-compliance parameter exists.
    params = policy.evaluate.__code__.co_varnames
    assert "model_compliant" not in params
    assert "override" not in params


def test_missing_budget_is_within_and_flagged():
    # verifies: RP-09 — no configured budget -> within_budget, missing_budget flagged.
    policy = BudgetPolicy({})
    statuses = policy.evaluate([_record("r1", "other", "10")])
    other = statuses[0]
    assert other.status == STATUS_WITHIN
    assert other.missing_budget is True
    assert other.limit is None
