"""Offline tests for ledger persistence.

Verifies: FR-005, RP-07, RP-08, SEC-001.
"""

from decimal import Decimal
from pathlib import Path

from pennyguard.ledger import LedgerStore
from pennyguard.models import CategorizationResult, GuardrailDecision, LedgerState


def _state() -> LedgerState:
    record = CategorizationResult(
        transaction_id="r1",
        description="Coffee",
        amount=Decimal("12.50"),
        category="food",
        source="rule",
        guardrail=GuardrailDecision(accepted=True, category="food", reason_code="OK"),
    )
    return LedgerState(transactions=[record], budgets={"food": Decimal("500")})


def test_roundtrip_consistent(tmp_path: Path):
    # verifies: FR-005 — reload produces identical transactions and budgets.
    store = LedgerStore(tmp_path / "ledger.json")
    store.save(_state())
    reloaded = store.load()
    assert len(reloaded.transactions) == 1
    assert reloaded.transactions[0].description == "Coffee"
    assert reloaded.transactions[0].amount == Decimal("12.50")
    assert reloaded.budgets["food"] == Decimal("500")


def test_missing_file_starts_empty(tmp_path: Path):
    # verifies: RP-07
    store = LedgerStore(tmp_path / "missing.json")
    state = store.load()
    assert state.transactions == []
    assert state.budgets == {}


def test_corrupt_file_recovers(tmp_path: Path):
    # verifies: RP-08 — corrupt file backed up, starts empty.
    path = tmp_path / "ledger.json"
    path.write_text("{ not valid json", encoding="utf-8")
    store = LedgerStore(path)
    state = store.load()
    assert state.transactions == []
    assert path.with_suffix(".corrupt.json").exists()


def test_no_secret_in_persisted_text(tmp_path: Path):
    # verifies: SEC-001 — persisted ledger text contains no secret.
    secret = "sk-secret-123"
    store = LedgerStore(tmp_path / "ledger.json")
    store.save(_state())
    persisted = store.redact_persisted(path_text(tmp_path / "ledger.json"), secret)
    assert secret not in persisted


def path_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")
