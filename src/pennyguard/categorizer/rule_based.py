"""Deterministic rule-based fallback categorizer.

ADR: ADR-001
Implements: FR-003, INV-005, COST-002, R-01

Always available offline; no network, no randomness. Unknown descriptions map to the
reserved `other` category rather than guessing.
"""

from __future__ import annotations

from ..models import (
    CATEGORIES,
    CandidateCategory,
    FALLBACK_CATEGORY,
    SOURCE_RULE,
    Transaction,
)
from .base import Categorizer

# Keyword -> category table. Order matters: first match wins; keep entries specific.
_KEYWORDS: dict[str, tuple[str, ...]] = {
    "food": (
        "coffee", "cafe", "cafeteria", "restaurant", "noodle", "bakery", "grocery",
        "food", "meal", "burger", "tea", "snack", "supermarket", "dining", "pizza",
    ),
    "transport": (
        "taxi", "bus", "metro", "subway", "train", "fuel", "gas", "ride", "uber",
        "lyft", "parking", "flight", "ferry", "tram", "metrocard", "mtr", "rail",
    ),
    "shopping": (
        "amazon", "amzn", "mktpl", "store", "mall", "shop", "clothing", "market",
        "order", "retail", "electronics", "bookstore", "shopping",
    ),
    "entertainment": (
        "movie", "cinema", "game", "concert", "gym", "netflix", "spotify", "theatre",
        "theater", "stadium", "bowling", "amusement",
    ),
    "housing": (
        "rent", "landlord", "mortgage", "furniture", "repair", "repairman", "deposit",
        "housing",
    ),
    "health": (
        "pharmacy", "doctor", "hospital", "clinic", "dental", "medicine", "dentist",
        "optician", "pharmacy",
    ),
    "utilities": (
        "electricity", "water", "internet", "phone", "bill", "utility", "gas bill",
        "broadband", "mobile",
    ),
}


class RuleBasedCategorizer(Categorizer):
    """Keyword/substring fallback categorizer (deterministic)."""

    def categorize(self, transaction: Transaction) -> CandidateCategory:
        text = transaction.description.lower()
        for category, keywords in _KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                return CandidateCategory(
                    category=category,
                    source=SOURCE_RULE,
                    raw_label=category,
                )
        return CandidateCategory(
            category=FALLBACK_CATEGORY,
            source=SOURCE_RULE,
            raw_label=FALLBACK_CATEGORY,
        )


def assert_whitelist_coverage() -> None:
    """Structural sanity: every keyword key is a whitelist category (fitness check)."""
    for category in _KEYWORDS:
        if category not in CATEGORIES:
            raise ValueError(f"Rule table references non-whitelist category '{category}'")
