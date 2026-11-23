"""Deterministic guardrail — the authority layer over advisory model output.

ADR: ADR-001
Implements: INV-001, INV-002, INV-004, INV-006, QA-003, SEC-002

This module accepts/rejects candidates against the closed whitelist, conserves the
transaction amount, and structurally validates responses. It exposes no budget-write,
ledger-write, deletion, shell, or tool-call surface (frozen safety-critical path).
"""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from .config import Config
from .models import (
    CATEGORIES,
    CandidateCategory,
    FALLBACK_CATEGORY,
    GuardrailDecision,
    SOURCES,
    Transaction,
)

# Reason codes (stable audit trail, QA-003).
REASON_OK = "OK"
REASON_NOT_IN_WHITELIST = "NOT_IN_WHITELIST"
REASON_MALFORMED = "MALFORMED_RESPONSE"
REASON_AMOUNT_IGNORED = "AMOUNT_OVERRIDE_IGNORED"


class Guardrail:
    """Deterministic validation applied to every categorization candidate."""

    def __init__(self, config: Config) -> None:
        self.config = config

    def validate_candidate(
        self, candidate: CandidateCategory, transaction: Transaction
    ) -> GuardrailDecision:
        # INV-004: structural validation — required fields present, legal types/enums.
        if not isinstance(candidate.category, str) or not candidate.category.strip():
            return GuardrailDecision(
                accepted=False,
                category=FALLBACK_CATEGORY,
                reason_code=REASON_MALFORMED,
                note="Candidate category is missing or not a string",
            )
        if candidate.source not in SOURCES:
            return GuardrailDecision(
                accepted=False,
                category=FALLBACK_CATEGORY,
                reason_code=REASON_MALFORMED,
                note=f"Unknown provenance source '{candidate.source}'",
            )

        # INV-001: closed whitelist check. Out-of-whitelist labels are rejected -> other.
        if candidate.category not in CATEGORIES:
            return GuardrailDecision(
                accepted=False,
                category=FALLBACK_CATEGORY,
                reason_code=REASON_NOT_IN_WHITELIST,
                note=f"Category '{candidate.category}' is outside the whitelist",
            )

        # INV-002: the model-supplied amount, if any, is discarded; conservation is
        # confirmed against the input transaction amount in check_amount_conservation.
        if candidate.model_amount is not None:
            return GuardrailDecision(
                accepted=True,
                category=candidate.category,
                reason_code=REASON_AMOUNT_IGNORED,
                note="Model-supplied amount ignored; input amount conserved",
            )

        return GuardrailDecision(
            accepted=True,
            category=candidate.category,
            reason_code=REASON_OK,
            note="Candidate accepted by guardrail",
        )

    @staticmethod
    def check_amount_conservation(input_amount: Decimal, stored_amount: Decimal) -> bool:
        """INV-002: stored amount must equal the input amount exactly."""
        return input_amount == stored_amount

    @staticmethod
    def redact(text: str, secret: Optional[str]) -> str:
        """SEC-001: mask any occurrence of the secret before logging/persisting."""
        if not secret:
            return text
        return text.replace(secret, "[REDACTED]")
