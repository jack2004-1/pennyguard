"""Configuration loading for PennyGuard.

ADR: ADR-001
Implements: FR-001, SEC-001, COST-001, PERF-002

Secrets are read only from the environment. No secret literal is stored in code,
config files, prompts, or the ledger (SEC-001).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from decimal import Decimal
from typing import Mapping, Optional

from .models import CATEGORIES

# Default monthly per-category budgets (currency unit-agnostic; exact decimal arithmetic).
DEFAULT_BUDGETS: dict[str, Decimal] = {
    "food": Decimal("500"),
    "transport": Decimal("200"),
    "shopping": Decimal("300"),
    "entertainment": Decimal("150"),
    "housing": Decimal("1500"),
    "health": Decimal("200"),
    "utilities": Decimal("250"),
    "other": Decimal("100"),
}

DEFAULT_TIMEOUT_S = 8.0          # PERF-002 hard LLM timeout
DEFAULT_TOKEN_BUDGET = 600        # COST-001 prompt cap (token-equivalent units)
DEFAULT_COMPACTION_THRESHOLD = 480  # 80% of budget


@dataclass(frozen=True)
class Config:
    categories: frozenset[str]
    budgets: dict[str, Decimal]
    endpoint: Optional[str]
    api_key: Optional[str]
    model: str
    timeout_s: float
    token_budget: int
    compaction_threshold: int

    @property
    def has_llm(self) -> bool:
        """True only when both an endpoint and a key are configured (FR-003, COST-002)."""
        return bool(self.endpoint and self.api_key)

    @classmethod
    def from_env(
        cls,
        env: Optional[Mapping[str, str]] = None,
        budgets: Optional[dict[str, Decimal]] = None,
    ) -> "Config":
        source: Mapping[str, str] = env if env is not None else os.environ
        api_key = source.get("LLM_API_KEY") or None
        endpoint = source.get("LLM_ENDPOINT") or None
        model = source.get("LLM_MODEL") or "default"

        parsed_budgets = dict(DEFAULT_BUDGETS)
        if budgets:
            parsed_budgets.update(budgets)
        # Guard: budget keys must be within the whitelist.
        for key in parsed_budgets:
            if key not in CATEGORIES:
                raise ValueError(f"Budget category '{key}' is not in the whitelist")

        return cls(
            categories=CATEGORIES,
            budgets=parsed_budgets,
            endpoint=endpoint,
            api_key=api_key,
            model=model,
            timeout_s=DEFAULT_TIMEOUT_S,
            token_budget=DEFAULT_TOKEN_BUDGET,
            compaction_threshold=DEFAULT_COMPACTION_THRESHOLD,
        )
