# Memory / State Design (D2.5)

Defines what state survives across sessions, interruptions, and versions; its read/write
policy, ownership, retention, and privacy handling.

## 1. State inventory

| State | Lifetime | Storage | Owner | Read policy | Write policy |
|---|---|---|---|---|---|
| Transactions (description, amount, date, category, provenance, guardrail reason) | Persistent across sessions/restarts | Local JSON ledger file (`ledger.json` under data dir) | `ledger.py` | Read only via `LedgerStore`; other modules receive records, not the file handle. | Written only after guardrail + policy accept the record. |
| Per-category monthly budgets | Persistent | Same ledger JSON (or user config) | `budget.py` (read), user config/command (write) | Policy reads budgets at evaluation time. | Changed only by user config or explicit user command; no AI write path (INV-006). |
| Pending record id / current month (resumable state) | Session, recoverable after interruption | In-memory + sidecar state file | `app.py` | Used to assemble resumable context for the prompt. | Updated by the pipeline after each accepted record. |
| Conversation history for the prompt | Session only, truncated | In-memory ring buffer | `prompt.py` | Included in assembly under budget; never persisted. | Truncated/compacted per COST-001; not written to disk. |
| Runtime configuration (endpoint, timeout, token budget, whitelist) | Persistent | Config file + environment | `config.py` | Loaded once at startup; immutable during a run. | Edited by the user; secrets come from env only. |
| Evaluation fixture set | Versioned with code | `test/offline/` fixtures / `eval.py` | `eval.py` | Replayed deterministically. | Changed only with the eval set version bump. |

## 2. Cross-session survival
- The ledger is the only business state that survives restart. On startup `ledger.py` loads
  the JSON; a missing or corrupt file falls back to an empty ledger and records a recovery
  event (see runtime policy catalog).
- Resumable state lets an interrupted run continue from the pending record; it is rebuilt
  from the last persisted ledger state rather than trusted in-memory only.

## 3. Interruption handling
- Each accepted record is persisted before the next record is processed, so a crash loses at
  most the in-flight record.
- Budget status is recomputed from persisted transactions on load (no derived status is
  trusted as durable).
- Prompt history is never required for recovery; losing it only reduces context, never
  corrupts the ledger.

## 4. Version evolution
- Ledger JSON carries a `schema_version` field. On load, a newer/unknown version is flagged;
  migration is an explicit, reviewed change (no silent rewrite).
- Code changes that add/rename a persisted field must update the ledger schema and the
  round-trip test in the same change.

## 5. Privacy and retention
- **No secret is persisted**: the API key exists only in the process environment and is
  redacted from logs, prompts, and the ledger (SEC-001).
- Transaction data stays local to the user's machine; the baseline has no telemetry,
  analytics, or outbound sync.
- Retention: the ledger is retained until the user deletes it; history buffers are cleared
  when the process exits.
- The model-facing prompt contains only the description being categorized and read-only
  context; it never includes stored secrets or unrelated persisted records beyond the
  budget-truncated recent history.
