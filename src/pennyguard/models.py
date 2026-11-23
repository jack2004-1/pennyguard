"""Domain records and closed whitelist for PennyGuard.

ADR: ADR-001
Implements: FR-001, FR-002, INV-001, QA-003

Modules exchange these typed records across boundaries; raw dicts stay inside a module.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Optional

# Closed category whitelist (INV-001). Adding a category is a configuration/architecture change,
# not an AI free-form choice.
CATEGORIES: frozenset[str] = frozenset(
    {
        "food",
        "transport",
        "shopping",
        "entertainment",
        "housing",
        "health",
        "utilities",
        "other",
    }
)

# Reserved fallback category when a candidate cannot be accepted.
FALLBACK_CATEGORY = "other"

# Provenance sources (QA-003).
SOURCE_LLM = "llm"
SOURCE_RULE = "rule"
SOURCE_FALLBACK = "fallback"
SOURCES = frozenset({SOURCE_LLM, SOURCE_RULE, SOURCE_FALLBACK})

# Budget statuses (INV-003).
STATUS_WITHIN = "within_budget"
STATUS_OVER = "over_budget"


def _parse_iso_date(value: str) -> str:
    """Validate an ISO YYYY-MM-DD date and return its normalized string.

    Raises ValueError on an unparseable date (R-08).
    """
    parsed = date.fromisoformat(value)
    return parsed.isoformat()


@dataclass(frozen=True)
class Transaction:
    """A single expense record. Amount is immutable after construction (INV-002)."""

    id: str
    description: str
    amount: Decimal
    date: str

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("Transaction.id must be non-empty")
        if not self.description:
            raise ValueError("Transaction.description must be non-empty")
        if self.amount < 0:
            raise ValueError("Transaction.amount must be non-negative")
        object.__setattr__(self, "date", _parse_iso_date(self.date))


@dataclass(frozen=True)
class CandidateCategory:
    """Advisory candidate produced by a categorizer. Not yet accepted by the guardrail."""

    category: str
    source: str
    raw_label: Optional[str] = None
    # Any model-supplied amount is recorded here only to be discarded by the guardrail (INV-002).
    model_amount: Optional[Decimal] = None


@dataclass(frozen=True)
class GuardrailDecision:
    """Deterministic guardrail verdict on a candidate (INV-001/002/004)."""

    accepted: bool
    category: str
    reason_code: str
    note: str = ""


@dataclass(frozen=True)
class CategorizationResult:
    """Accepted record stored in the ledger, with provenance and guardrail decision."""

    transaction_id: str
    description: str
    amount: Decimal
    category: str
    source: str
    guardrail: GuardrailDecision


@dataclass(frozen=True)
class Budget:
    """Per-category monthly budget limit."""

    category: str
    limit: Decimal


@dataclass(frozen=True)
class BudgetStatus:
    """Deterministic compliance status owned by BudgetPolicy (INV-003)."""

    category: str
    spent: Decimal
    limit: Optional[Decimal]
    status: str
    missing_budget: bool = False


@dataclass
class LedgerState:
    """Serializable ledger state persisted to local JSON (FR-005)."""

    transactions: list[CategorizationResult] = field(default_factory=list)
    budgets: dict[str, Decimal] = field(default_factory=dict)
    schema_version: int = 1
