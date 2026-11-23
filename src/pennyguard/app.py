"""Application assembly and CLI orchestration.

ADR: ADR-001
Implements: FR-003, FR-007, INV-005, SEC-001

Flow: select categorizer -> guardrail validates candidate -> BudgetPolicy owns compliance ->
ledger persists. The advisory layer never reaches budget/ledger mutation directly.
"""

from __future__ import annotations

import argparse
import uuid
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Optional

from .budget import BudgetPolicy
from .categorizer.base import Categorizer, CategorizerError
from .categorizer.rule_based import RuleBasedCategorizer
from .config import Config
from .eval import Evaluator
from .guardrail import Guardrail
from .ledger import LedgerStore
from .models import (
    CategorizationResult,
    CandidateCategory,
    FALLBACK_CATEGORY,
    LedgerState,
    SOURCE_FALLBACK,
    SOURCE_RULE,
    Transaction,
)


class ExpenseApp:
    """Wires configuration, guardrail, policy, ledger, and the selected categorizer."""

    def __init__(
        self,
        config: Config,
        ledger: LedgerStore,
        guardrail: Optional[Guardrail] = None,
        policy: Optional[BudgetPolicy] = None,
        categorizer: Optional[Categorizer] = None,
        state: Optional[LedgerState] = None,
    ) -> None:
        self.config = config
        self.ledger = ledger
        self.guardrail = guardrail or Guardrail(config)
        self.policy = policy or BudgetPolicy(config.budgets)
        self._rule = RuleBasedCategorizer()
        self._injected_categorizer = categorizer
        self.state = state or ledger.load()

    # -- core pipeline -------------------------------------------------------

    def add_transaction(self, description: str, amount: str, date: str) -> CategorizationResult:
        amount_decimal = self._parse_amount(amount)
        tx = Transaction(
            id=uuid.uuid4().hex[:10],
            description=description.strip(),
            amount=amount_decimal,
            date=date,
        )

        candidate = self._produce_candidate(tx)
        decision = self.guardrail.validate_candidate(candidate, tx)

        if not decision.accepted:
            # Rejected candidate: replace with the reserved fallback and re-validate (INV-001).
            fallback = CandidateCategory(category=FALLBACK_CATEGORY, source=SOURCE_FALLBACK)
            decision = self.guardrail.validate_candidate(fallback, tx)

        # INV-002: stored amount must equal the input amount exactly.
        if not self.guardrail.check_amount_conservation(tx.amount, tx.amount):
            raise ValueError("Amount conservation failed")

        result = CategorizationResult(
            transaction_id=tx.id,
            description=tx.description,
            amount=tx.amount,
            category=decision.category,
            source=candidate.source if decision.reason_code == "OK" else SOURCE_FALLBACK,
            guardrail=decision,
        )
        self.state.transactions.append(result)
        self.ledger.save(self.state)
        return result

    def _produce_candidate(self, tx: Transaction) -> CandidateCategory:
        """Select LLM when configured; degrade to rule-based on any failure (INV-005)."""
        try:
            if self._injected_categorizer is not None:
                return self._injected_categorizer.categorize(tx)
            if self.config.has_llm:
                from .categorizer.llm import LlmCategorizer

                return LlmCategorizer(self.config).categorize(tx)
            return self._rule.categorize(tx)
        except CategorizerError:
            # Fall through to deterministic rule-based fallback; no crash, no leak.
            return self._rule.categorize(tx)

    @staticmethod
    def _parse_amount(amount: str) -> Decimal:
        try:
            value = Decimal(str(amount).strip())
        except (InvalidOperation, ValueError) as exc:
            raise ValueError(f"Invalid amount: {amount!r}") from exc
        if value < 0:
            raise ValueError("Amount must be non-negative")
        return value

    # -- queries -------------------------------------------------------------

    def list_records(self) -> list[CategorizationResult]:
        return list(self.state.transactions)

    def status(self):
        return self.policy.evaluate(self.state.transactions)

    def evaluate(self) -> dict:
        categorizer = self._injected_categorizer or self._rule
        return Evaluator(categorizer, self.guardrail).run().as_dict()


# -- CLI ---------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pennyguard", description="AI-assisted expense guardrail CLI")
    sub = parser.add_subparsers(dest="command")

    p_add = sub.add_parser("add", help="Add a transaction")
    p_add.add_argument("--description", required=True)
    p_add.add_argument("--amount", required=True)
    p_add.add_argument("--date", required=True, help="ISO date YYYY-MM-DD")

    sub.add_parser("list", help="List recorded transactions")
    sub.add_parser("status", help="Show per-category budget status")
    sub.add_parser("eval", help="Replay the fixed evaluation set")
    return parser


def main(argv: Optional[list[str]] = None, data_dir: Optional[Path] = None) -> int:
    config = Config.from_env()
    base = data_dir or Path(".pennyguard")
    ledger = LedgerStore(base / "ledger.json")
    app = ExpenseApp(config, ledger)

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "add":
        result = app.add_transaction(args.description, args.amount, args.date)
        print(
            f"Added {result.transaction_id}: {result.description} -> "
            f"{result.category} [{result.source}] ({result.guardrail.reason_code})"
        )
        return 0
    if args.command == "list":
        for r in app.list_records():
            print(f"{r.transaction_id} | {r.description} | {r.amount} | {r.category} | {r.source}")
        return 0
    if args.command == "status":
        for s in app.status():
            print(f"{s.category}: spent={s.spent} limit={s.limit} status={s.status}")
        return 0
    if args.command == "eval":
        print(app.evaluate())
        return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
