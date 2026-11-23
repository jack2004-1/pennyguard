# Runtime Policy Catalog (D2.7)

What the system does when each degraded or failure path triggers. Policies are deterministic
and owned by the authoritative layer; the model cannot override them.

| # | Failure / degraded path | Detection point | System action | Fallback | Monitor event |
|---|---|---|---|---|---|
| RP-01 | No API key or endpoint configured | `config.py` / `app.py` at categorizer selection | Do not construct an LLM client; select rule-based classifier. | Run fully offline. | `categorizer=rule`, reason `NO_CONFIG` |
| RP-02 | LLM call timeout (> 8 s) | `categorizer/llm.py` client timeout | Abort the call; degrade to rule-based classifier. | Rule-based result for the record. | `degraded`, reason `TIMEOUT` |
| RP-03 | LLM transport error (connection, 5xx, network) | LLM client exception handler | Catch exception; degrade to fallback; do not crash. | Rule-based result. | `degraded`, reason `TRANSPORT_ERROR` |
| RP-04 | LLM payload malformed (missing field, wrong type, illegal enum) | `guardrail.validate_candidate` | Reject candidate as a failed model call; route to fallback. | Rule-based result; record `MALFORMED_RESPONSE`. | `guardrail_rejected`, reason `MALFORMED_RESPONSE` |
| RP-05 | Model category outside whitelist | `guardrail.validate_category` | Reject label; replace with reserved `other`. | `other` category; persist accepted record. | `guardrail_rejected`, reason `NOT_IN_WHITELIST` |
| RP-06 | Model supplies an amount field | `guardrail.check_amount_conservation` | Discard model amount; keep input amount. | Continue with conserved amount. | `amount_override_ignored` |
| RP-07 | Ledger file missing on startup | `ledger.load` | Start from an empty ledger; do not fail. | Empty in-memory ledger; save on next write. | `ledger_recovered`, reason `MISSING_FILE` |
| RP-08 | Ledger file corrupt / unparseable | `ledger.load` parse/validation | Back up the corrupt file under a recovery name; start empty; flag user. | Empty ledger; warn in output. | `ledger_recovered`, reason `CORRUPT_FILE` |
| RP-09 | No budget configured for a category | `budget.evaluate` | Treat budget as unlimited for that category; status `within_budget`; warn. | Record with no over-budget flag. | `budget_missing`, category recorded |
| RP-10 | Assembled prompt exceeds token budget | `prompt.assemble` after compaction | Re-run compaction; if still over, drop non-constraint history/examples; re-inject constraints. | Send a budget-compliant prompt; never exceed cap. | `prompt_compacted`, size recorded |
| RP-11 | Evaluation fixture missing or empty | `eval.run` | Report an empty/zero run without failing the suite; surface a clear message. | Skip semantic thresholds for that run. | `eval_empty` |
| RP-12 | Unknown CLI sub-command | `app.py` parser | Print documented usage; exit with non-zero documented code. | No ledger mutation. | `cli_unknown_command` |
| RP-13 | Boundary attempt to write budget or call privileged action from model path | Package boundary / guardrail | Block the call; raise `BoundaryViolation`; record security event. | No mutation; transaction processed via fallback only. | `security_event`, reason `BOUNDARY_VIOLATION` |
| RP-14 | Secret appears in a message to be logged/persisted | Redaction routine before write | Mask any occurrence of the key before output/persistence. | Continue with redacted string. | `secret_redacted` |

## Policy rules
- Every degradation keeps the system in a safe, consistent state: no partial privileged
  mutation, no crash on model failure, no secret leakage.
- Fallbacks are observable: each event carries a stable reason code for the audit trail.
- A policy path that repeatedly triggers should be reviewed in a bug diary entry and, if it
  reflects a missing invariant, added to the invariant register.
