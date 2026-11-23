"""Categorizer interface — the sole classification contract (structural constraints §1).

ADR: ADR-001
Implements: FR-002, INV-004

Both the rule-based fallback and the optional LLM implementation conform to this interface.
The advisory layer produces a CandidateCategory only; it has no budget, ledger, or privileged
action surface (INV-006, SEC-002).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..models import CandidateCategory, Transaction


class CategorizerError(Exception):
    """Raised when a categorizer cannot produce a candidate; callers degrade to fallback."""


class Categorizer(ABC):
    """Abstract categorizer. Implementations must be safe to call offline where possible."""

    @abstractmethod
    def categorize(self, transaction: Transaction) -> CandidateCategory:
        """Return an advisory candidate for the transaction description."""
        raise NotImplementedError
