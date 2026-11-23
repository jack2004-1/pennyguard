"""Deterministic budget policy — sole authority on compliance status.

ADR: ADR-001
Implements: FR-004, INV-003

Over/under-budget decisions are computed here with exact decimal arithmetic. The AI cannot
raise a budget or flip an over-budget flag to compliant; this module exposes no model-facing
write path (frozen safety-critical path).
"""

from __future__ import annotations

from decimal import Decimal

from .models import BudgetStatus, CategorizationResult, STATUS_OVER, STATUS_WITHIN


class BudgetPolicy:
    """Computes per-category spending and compliance from persisted records."""

    def __init__(self, budgets: dict[str, Decimal]) -> None:
        self._budgets = dict(budgets)

    def evaluate(self, transactions: list[CategorizationResult]) -> list[BudgetStatus]:
        spent: dict[str, Decimal] = {}
        for record in transactions:
            spent[record.category] = spent.get(record.category, Decimal("0")) + record.amount

        statuses: list[BudgetStatus] = []
        categories = sorted(set(spent) | set(self._budgets))
        for category in categories:
            statuses.append(self._status_for(category, spent.get(category, Decimal("0"))))
        return statuses

    def _status_for(self, category: str, spent: Decimal) -> BudgetStatus:
        limit = self._budgets.get(category)
        if limit is None:
            # RP-09: no configured budget -> treat as unlimited, flag missing_budget.
            return BudgetStatus(
                category=category,
                spent=spent,
                limit=None,
                status=STATUS_WITHIN,
                missing_budget=True,
            )
        if spent > limit:
            return BudgetStatus(
                category=category, spent=spent, limit=limit, status=STATUS_OVER
            )
        return BudgetStatus(
            category=category, spent=spent, limit=limit, status=STATUS_WITHIN
        )

    def status_for(self, category: str, spent: Decimal) -> BudgetStatus:
        """Public deterministic evaluation for a single category."""
        return self._status_for(category, spent)
