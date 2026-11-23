"""Offline degradation tests for LLM failure modes.

Verifies: INV-005, PERF-002, SEC-001.
"""

from decimal import Decimal
from pathlib import Path

import pytest

from pennyguard.app import ExpenseApp
from pennyguard.categorizer.base import Categorizer, CategorizerError
from pennyguard.categorizer.llm import LlmCategorizer
from pennyguard.config import Config
from pennyguard.ledger import LedgerStore
from pennyguard.models import CATEGORIES, Transaction

LLM_ENV = {"LLM_API_KEY": "sk-test-secret", "LLM_ENDPOINT": "http://localhost/v1/chat"}


class _TimeoutClient:
    def complete(self, messages):
        raise TimeoutError("timed out")


class _TransportErrorClient:
    def complete(self, messages):
        raise ConnectionError("unreachable")


class _RaisingCategorizer(Categorizer):
    def categorize(self, transaction: Transaction):
        raise CategorizerError("model unavailable")


def _tx() -> Transaction:
    return Transaction(id="t1", description="Coffee", amount=Decimal("10"), date="2026-11-01")


def test_llm_timeout_degrades():
    # verifies: PERF-002 — timeout surfaces as CategorizerError for the app to degrade.
    config = Config.from_env(env=LLM_ENV)
    llm = LlmCategorizer(config, client=_TimeoutClient())
    try:
        llm.categorize(_tx())
        assert False, "expected CategorizerError"
    except CategorizerError:
        pass


def test_llm_transport_error_degrades():
    # verifies: INV-005 — transport error surfaces as CategorizerError.
    config = Config.from_env(env=LLM_ENV)
    llm = LlmCategorizer(config, client=_TransportErrorClient())
    try:
        llm.categorize(_tx())
        assert False, "expected CategorizerError"
    except CategorizerError:
        pass


def test_app_degrades_to_rule_on_failure(tmp_path: Path):
    # verifies: INV-005 — app catches failure and returns a valid fallback result.
    config = Config.from_env(env=LLM_ENV)
    ledger = LedgerStore(tmp_path / "ledger.json")
    app = ExpenseApp(config, ledger, categorizer=_RaisingCategorizer())
    result = app.add_transaction("Coffee shop", "10.00", "2026-11-01")
    assert result.category in CATEGORIES
    assert result.guardrail.accepted is True


def test_no_secret_leaked_in_result_or_ledger(tmp_path: Path):
    # verifies: SEC-001 / INV-005 — secret never appears in result or persisted ledger.
    config = Config.from_env(env=LLM_ENV)
    ledger = LedgerStore(tmp_path / "ledger.json")
    app = ExpenseApp(config, ledger, categorizer=_RaisingCategorizer())
    result = app.add_transaction("Coffee shop", "10.00", "2026-11-01")
    assert "sk-test-secret" not in str(result)
    persisted = (tmp_path / "ledger.json").read_text(encoding="utf-8")
    assert "sk-test-secret" not in persisted


def test_llm_failure_modes_degrade_cleanly(tmp_path: Path):
    # verifies: INV-005 — every LLM failure mode degrades cleanly without crash or leak.
    config = Config.from_env(env=LLM_ENV)

    for client in (_TimeoutClient(), _TransportErrorClient()):
        llm = LlmCategorizer(config, client=client)
        with pytest.raises(CategorizerError):
            llm.categorize(_tx())

    ledger = LedgerStore(tmp_path / "ledger.json")
    app = ExpenseApp(config, ledger, categorizer=_RaisingCategorizer())
    result = app.add_transaction("Coffee shop", "10.00", "2026-11-01")
    assert result.category in CATEGORIES
    assert result.guardrail.accepted is True
    persisted = (tmp_path / "ledger.json").read_text(encoding="utf-8")
    assert "sk-test-secret" not in persisted
