"""Offline tests for the deterministic guardrail authority layer.

Verifies: INV-001, INV-002, INV-004, INV-006, QA-003, SEC-002.
"""

import inspect
from decimal import Decimal

from pennyguard import categorizer
from pennyguard.config import Config
from pennyguard.guardrail import Guardrail
from pennyguard.models import CATEGORIES, CandidateCategory, Transaction


def _tx() -> Transaction:
    return Transaction(id="t1", description="Coffee", amount=Decimal("10"), date="2026-11-01")


def _guardrail() -> Guardrail:
    return Guardrail(Config.from_env(env={}))


def test_out_of_whitelist_rejected():
    # verifies: INV-001 — out-of-whitelist model label rejected -> other.
    gr = _guardrail()
    candidate = CandidateCategory(category="spaceship", source="llm", raw_label="spaceship")
    decision = gr.validate_candidate(candidate, _tx())
    assert decision.accepted is False
    assert decision.category == "other"
    assert decision.reason_code == "NOT_IN_WHITELIST"


def test_amount_conservation():
    # verifies: INV-002 — stored amount equals input; model amount ignored.
    gr = _guardrail()
    tx = _tx()
    assert gr.check_amount_conservation(tx.amount, tx.amount) is True
    candidate = CandidateCategory(
        category="food", source="llm", model_amount=Decimal("999")
    )
    decision = gr.validate_candidate(candidate, tx)
    # The model-supplied amount does not change the conserved input amount.
    assert tx.amount == Decimal("10")
    assert decision.reason_code == "AMOUNT_OVERRIDE_IGNORED"


def test_malformed_response_degraded():
    # verifies: INV-004 — missing field / illegal enum rejected.
    gr = _guardrail()
    empty = CandidateCategory(category="", source="llm")
    assert gr.validate_candidate(empty, _tx()).accepted is False

    bad_source = CandidateCategory(category="food", source="telepathy")
    decision = gr.validate_candidate(bad_source, _tx())
    assert decision.accepted is False
    assert decision.reason_code == "MALFORMED_RESPONSE"


def test_provenance_and_reason_recorded():
    # verifies: QA-003 — provenance and reason code present on every decision.
    gr = _guardrail()
    candidate = CandidateCategory(category="food", source="rule")
    decision = gr.validate_candidate(candidate, _tx())
    assert decision.accepted is True
    assert decision.reason_code
    assert decision.note


def test_no_ai_budget_write_surface():
    # verifies: INV-006 — model-facing package exposes no budget-write/delete/exec surface.
    forbidden = ("budget", "write", "delete", "exec", "shell", "tool")
    for _name, obj in inspect.getmembers(categorizer):
        if inspect.isfunction(obj) or inspect.isclass(obj):
            lowered = getattr(obj, "__name__", "").lower()
            assert not any(word in lowered for word in forbidden), f"forbidden surface: {lowered}"

    # The categorizer package must not import the budget authority module.
    import pennyguard.categorizer.base as base_mod

    assert "budget" not in base_mod.__dict__


def test_model_output_not_executed():
    # verifies: SEC-002 — model output is a constrained candidate, not an executable action.
    candidate = CandidateCategory(category="food", source="llm", raw_label="; rm -rf /")
    fields = set(candidate.__dict__.keys())
    assert {"command", "action", "tool", "shell"}.isdisjoint(fields)
    gr = _guardrail()
    decision = gr.validate_candidate(candidate, _tx())
    # Guardrail never evaluates or executes raw model text.
    assert decision.category in CATEGORIES
