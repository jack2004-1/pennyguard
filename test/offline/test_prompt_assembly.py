"""Offline tests for prompt assembly budget and compaction.

Verifies: COST-001, RP-10.
"""

from decimal import Decimal

from pennyguard.config import Config
from pennyguard.models import Transaction
from pennyguard.prompt import PromptAssembler


def _tx(desc: str = "Coffee shop") -> Transaction:
    return Transaction(id="t1", description=desc, amount=Decimal("10"), date="2026-11-01")


def test_prompt_within_budget():
    # verifies: COST-001 — assembled prompt stays within the token cap.
    config = Config.from_env(env={})
    assembler = PromptAssembler(config)
    assembled = assembler.assemble(_tx())
    assert assembled.token_estimate <= config.token_budget
    assert len(assembled.messages) == 2


def test_standing_constraints_present():
    # verifies: ADR-001 §6.1 — identity and standing constraints are in the context.
    config = Config.from_env(env={})
    assembled = PromptAssembler(config).assemble(_tx())
    system = assembled.messages[0]["content"]
    assert "Whitelist" in system
    assert "Do not perform any action" in system


def test_long_history_compacted_constraints_retained():
    # verifies: COST-001 / RP-10 — over-threshold history is compacted; constraints re-injected.
    config = Config.from_env(env={})
    assembler = PromptAssembler(config)
    long_history = ["prior expense note " * 5] * 40
    assembled = assembler.assemble(_tx("Uber ride"), history=long_history)
    assert assembled.token_estimate <= config.token_budget
    system = assembled.messages[0]["content"]
    # Critical constraints survive compaction (re-injection policy).
    assert "Do not perform any action" in system
    assert "Whitelist" in system
