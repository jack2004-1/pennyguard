# Invariant Register (D2.3)

Zero-tolerance rules. Each invariant lists its statement, source requirement ID, enforcing
component, verification method, and the concrete operational fallback when violated. A test
that fails when the invariant is violated is required for every entry (D4).

| ID | Statement | Source req | Enforcing component | Verification method | Fallback when violated |
|---|---|---|---|---|---|
| INV-001 | Every assigned category belongs to the closed whitelist; an out-of-whitelist AI category is rejected and replaced with `other`. | INV-001, FR-002 | `guardrail.py` (`Guardrail.validate_category`) | Offline test injects an out-of-whitelist model label; asserts it is rejected, reason code `NOT_IN_WHITELIST`, and final category is `other`. | Reject the candidate, log reason `NOT_IN_WHITELIST`, assign reserved `other`, continue processing; do not persist the rejected label. |
| INV-002 | Amount conservation: the recorded amount equals the input amount; any model-supplied amount is ignored. | INV-002, FR-001 | `guardrail.py` (`Guardrail.check_amount_conservation`) | Offline test passes a transaction with a model-proposed amount differing from input; asserts stored amount equals input. | Discard any model amount field; keep the input amount; flag provenance `amount_override_ignored`; continue. |
| INV-003 | Over/under-budget decisions are made only by `BudgetPolicy`; the AI cannot raise a budget or flip an over-budget flag to compliant. | INV-003, FR-004 | `budget.py` (`BudgetPolicy.evaluate`) | Offline test attempts to make model output mark an over-budget record compliant; asserts status still comes from policy and remains `over_budget`. | Ignore any model compliance signal; recompute status from policy; record `compliance_override_rejected`. |
| INV-004 | Every AI response passes deterministic structural validation (required fields, correct types, legal enums); invalid responses degrade to fallback. | INV-004 | `guardrail.py` (`Guardrail.validate_candidate`) | Offline test feeds missing-field, wrong-type, and illegal-enum payloads; assert each is rejected and routed to fallback. | Treat as a failed model call; use rule-based categorizer; record reason `MALFORMED_RESPONSE`; do not crash. |
| INV-005 | On LLM unavailability (no key, timeout, transport error, invalid payload), degrade to fallback without crashing and without leaking the key. | INV-005, PERF-002, SEC-001 | `categorizer/llm.py`, `app.py` | Offline test simulates each failure mode; asserts fallback result, clean exit, and no secret in persisted/logged strings. | Catch the failure, switch to `RuleBasedCategorizer`, record source `fallback` and failure reason; redact secrets in any message. |
| INV-006 | Budget limits are changed only via user configuration or explicit user command; the AI-facing layer exposes no budget-write interface. | INV-006, SEC-002 | Package boundary: `categorizer/` must not import budget-mutating APIs; `guardrail.py` owns the accepted candidate. | Offline API-surface/structural test enumerates exported names of the model-facing package and asserts no budget-write method exists. | Block the call at the boundary; raise `BoundaryViolation`; record a security event; do not mutate any budget. |

## Enforcement notes
- Invariants are enforced in deterministic code, never trusted to the model's instruction
  following.
- Each fallback is a concrete action (reject / replace / discard / recompute / block), not a
  generic "fix the bug".
- A violation that reaches persistence indicates a guardrail gap; it must be logged in
  `docs/bug-diary.md` and traced to the missing invariant check.
