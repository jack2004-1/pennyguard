"""Prompt assembly pipeline for the optional LLM categorizer.

ADR: ADR-001 (§6 layered context, §6.2 assembly pipeline, §6.3 budget)
Implements: COST-001, INV-004, RP-10

Pipeline: dedup -> prioritize -> budget -> compact -> assemble -> validate.
Standing constraints and the whitelist are exempt from truncation and are re-injected
verbatim after compaction.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .config import Config
from .models import CATEGORIES, Transaction

# Standing constraints: non-trimmable, always re-injected after compaction.
_STANDING_CONSTRAINTS: tuple[str, ...] = (
    "You categorize one expense description into exactly one closed-budget category.",
    "Output category MUST be one of the whitelist labels; never invent a new label.",
    "Do not provide or infer an amount; amounts are handled by deterministic code.",
    "Do not perform any action, write a budget, delete a record, or call any tool.",
    "Respond with JSON only: {\"category\": \"<whitelist label>\", \"label\": \"<short label>\"}.",
)

_WHITELIST_DESCRIPTIONS: dict[str, str] = {
    "food": "restaurants, groceries, drinks, snacks, meals",
    "transport": "taxi, bus, metro, train, fuel, parking, flights",
    "shopping": "retail stores, online orders, clothing, electronics",
    "entertainment": "movies, games, concerts, gym, streaming",
    "housing": "rent, mortgage, furniture, home repairs",
    "health": "pharmacy, doctor, clinic, dental, medicine",
    "utilities": "electricity, water, internet, phone, bills",
    "other": "anything that does not fit the categories above",
}


def _token_estimate(text: str) -> int:
    """Rough token-equivalent estimate: ~4 characters per token (COST-001 budget unit)."""
    return max(1, len(text) // 4)


@dataclass
class AssembledPrompt:
    messages: list[dict[str, str]] = field(default_factory=list)
    token_estimate: int = 0
    compacted: bool = False


class PromptAssembler:
    """Assembles the layered context for one categorization turn within the token budget."""

    def __init__(self, config: Config) -> None:
        self.config = config

    def assemble(
        self,
        transaction: Transaction,
        history: Optional[list[str]] = None,
    ) -> AssembledPrompt:
        history = list(history or [])

        # 1. Dedup + prioritize: constraints > whitelist > current task > history.
        constraints = list(dict.fromkeys(_STANDING_CONSTRAINTS))
        whitelist_lines = [
            f"- {cat}: {_WHITELIST_DESCRIPTIONS[cat]}" for cat in sorted(CATEGORIES)
        ]
        current_task = f"Description: {transaction.description}"
        resumable_state = f"Ledger month: {transaction.date[:7]}; record id: {transaction.id}"

        # 2. Budget check; compact history/examples first if over threshold.
        compacted = False
        while self._size(constraints, whitelist_lines, current_task, resumable_state, history) > (
            self.config.compaction_threshold
        ) and history:
            history.pop(0)  # drop oldest history first
            compacted = True

        # 3. Re-inject critical constraints and whitelist verbatim after compaction.
        system_text = "\n".join(
            [
                "Identity: PennyGuard expense categorizer.",
                "Standing constraints:",
                *[f"- {c}" for c in constraints],
                "Whitelist:",
                *whitelist_lines,
            ]
        )
        user_text = "\n".join(
            [
                resumable_state,
                f"Recent history: {'; '.join(history)}" if history else "Recent history: (none)",
                current_task,
            ]
        )

        messages = [
            {"role": "system", "content": system_text},
            {"role": "user", "content": user_text},
        ]
        size = self._size_text(system_text) + self._size_text(user_text)

        # 4. Validate against hard cap; if still over, drop history entirely (RP-10).
        if size > self.config.token_budget and history:
            history.clear()
            compacted = True
            user_text = "\n".join([resumable_state, current_task])
            messages[1] = {"role": "user", "content": user_text}
            size = self._size_text(system_text) + self._size_text(user_text)

        return AssembledPrompt(messages=messages, token_estimate=size, compacted=compacted)

    @staticmethod
    def _size_text(text: str) -> int:
        return _token_estimate(text)

    def _size(
        self,
        constraints: list[str],
        whitelist_lines: list[str],
        current_task: str,
        resumable_state: str,
        history: list[str],
    ) -> int:
        blob = "\n".join(constraints + whitelist_lines + [current_task, resumable_state, *history])
        return _token_estimate(blob)
