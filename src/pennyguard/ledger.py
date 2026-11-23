"""Local JSON ledger persistence.

ADR: ADR-001
Implements: FR-005, SEC-001, RP-07, RP-08

The ledger is the only business state that survives restart. It stores no secret. A missing
file starts empty; a corrupt file is backed up and replaced with an empty state.
"""

from __future__ import annotations

import json
import shutil
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Optional

from .models import CategorizationResult, GuardrailDecision, LedgerState


class LedgerStore:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    def load(self) -> LedgerState:
        if not self.path.exists():
            return LedgerState()
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            return self._deserialize(raw)
        except (json.JSONDecodeError, ValueError, InvalidOperation, KeyError, TypeError):
            # RP-08: back up the corrupt file, then start empty.
            backup = self.path.with_suffix(".corrupt.json")
            shutil.copy2(self.path, backup)
            return LedgerState()

    def save(self, state: LedgerState) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(self._serialize(state), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    # -- serialization -------------------------------------------------------

    @staticmethod
    def _serialize(state: LedgerState) -> dict:
        return {
            "schema_version": state.schema_version,
            "budgets": {cat: str(limit) for cat, limit in state.budgets.items()},
            "transactions": [
                {
                    "transaction_id": r.transaction_id,
                    "description": r.description,
                    "amount": str(r.amount),
                    "category": r.category,
                    "source": r.source,
                    "guardrail": {
                        "accepted": r.guardrail.accepted,
                        "category": r.guardrail.category,
                        "reason_code": r.guardrail.reason_code,
                        "note": r.guardrail.note,
                    },
                }
                for r in state.transactions
            ],
        }

    @staticmethod
    def _deserialize(raw: dict) -> LedgerState:
        budgets = {
            cat: Decimal(limit) for cat, limit in raw.get("budgets", {}).items()
        }
        records: list[CategorizationResult] = []
        for item in raw.get("transactions", []):
            guard = item.get("guardrail", {})
            records.append(
                CategorizationResult(
                    transaction_id=item["transaction_id"],
                    description=item["description"],
                    amount=Decimal(item["amount"]),
                    category=item["category"],
                    source=item["source"],
                    guardrail=GuardrailDecision(
                        accepted=bool(guard.get("accepted", False)),
                        category=guard.get("category", "other"),
                        reason_code=guard.get("reason_code", ""),
                        note=guard.get("note", ""),
                    ),
                )
            )
        return LedgerState(transactions=records, budgets=budgets, schema_version=raw.get("schema_version", 1))

    @staticmethod
    def redact_persisted(text: str, secret: Optional[str]) -> str:
        """SEC-001: ensure no secret reaches a persisted string."""
        if not secret:
            return text
        return text.replace(secret, "[REDACTED]")
