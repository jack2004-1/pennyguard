"""Offline tests for domain records.

Verifies: FR-001 (structured record valid).
"""

from decimal import Decimal

import pytest

from pennyguard.models import Transaction


def test_transaction_record_valid():
    # verifies: FR-001
    tx = Transaction(id="t1", description="Coffee", amount=Decimal("12.50"), date="2026-11-01")
    assert tx.id == "t1"
    assert tx.description == "Coffee"
    assert tx.amount == Decimal("12.50")
    assert tx.amount >= 0
    assert tx.date == "2026-11-01"


def test_negative_amount_rejected():
    # negative test: invalid input must be rejected (INV-002 / FR-001)
    with pytest.raises(ValueError):
        Transaction(id="t2", description="Refund", amount=Decimal("-5"), date="2026-11-01")


def test_empty_description_rejected():
    # negative test: invalid input must be rejected
    with pytest.raises(ValueError):
        Transaction(id="t3", description="", amount=Decimal("5"), date="2026-11-01")


def test_bad_date_rejected():
    # negative test: unparseable ISO date rejected (R-08)
    with pytest.raises(ValueError):
        Transaction(id="t4", description="Thing", amount=Decimal("5"), date="not-a-date")
