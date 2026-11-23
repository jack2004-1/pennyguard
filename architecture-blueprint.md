# PennyGuard — Architecture Blueprint (D2.1)

> Master constraint document read first by the Plan/coding agent. It fixes scope,
> boundaries, components, authority split, agent workflow, permissions, verification,
> observability, and change policy. Where this document conflicts with a later ad-hoc
> agent suggestion, this document wins until an ADR amends it.

- **Project**: PennyGuard — AI-assisted personal-expense categorization with deterministic budget guardrails
- **Course**: CS5351 Agentic Software Engineering, 2026/27 Sem A
- **Author**: Yiyang BU (卜毅扬), Student ID 60392800, Group 43 (solo)
- **Status**: Baseline v1.0, 2026-11-23

## 1. Scope

### 1.1 In scope
- Import a transaction (free-text description, numeric amount, ISO date) into a local ledger.
- An **AI component** suggests a budget category from the description; a deterministic
  guardrail validates and constrains that suggestion.
- Per-category monthly budgets; deterministic over/under-budget status.
- Local JSON persistence surviving restarts; provenance recorded per record.
- A fixed offline evaluation set that replays the pipeline and reports faithfulness,
  relevance, and safety-escape counts.
- A CLI with `add`, `list`, `status`, `eval` sub-commands.

### 1.2 Out of scope (this baseline)
- Multi-user accounts, cloud sync, concurrency control, multi-currency conversion.
- Bank-feed / CSV import, receipt OCR, multi-label tagging.
- Any autonomous action by the model (no budget writes, no deletes, no shell/tool calls).

## 2. Architectural drivers

| Driver | Requirement(s) | Consequence |
|---|---|---|
| Auditable human supervision of AI code generation | GOV-002, GOV-003, D3/D5 | Governance files constrain the agent; every AI-assisted change logged and reviewed. |
| A genuine AI component with a hard safety boundary | FR-002, INV-001…006, SEC-002 | Model output is advisory; a deterministic guardrail layer sits between model and ledger. |
| Offline-deterministic, CI/grading friendly | FR-003, QA-001, COST-002, PERF-001 | Default path needs no network or secret; live LLM path is optional and isolated. |
| Traceability requirement → component → test → monitor | QA-002, GOV-001 | One module per architectural element; trace matrix maps every requirement. |
| Bounded LLM cost and latency | COST-001, PERF-002 | Prompt assembly with token budget, compaction, hard timeout, fallback. |

## 3. System boundaries

### 3.1 Context
```
                ┌──────────────────────────────────────────────────────┐
   user CLI ───▶│                        PennyGuard                    │
                │  app ─▶ ledger ─▶ budget policy ─▶ guardrail ─▶      │
                │            categorizer(base) ─▶ rule_based / llm      │
                │            prompt assembler ─▶ eval                   │
                └───────────────┬───────────────────────┬──────────────┘
                                │ optional, outbound     │ local only
                                ▼                       ▼
                     OpenAI-compatible LLM        local JSON ledger
                     (e.g. DeepSeek endpoint)      (no secret stored)
```

### 3.2 External dependencies
- **Optional LLM endpoint**: OpenAI-compatible chat completions API, reached only when
  `LLM_API_KEY` and endpoint are configured. Called through a thin client using the
  standard library; no SDK lock-in.
- **Local filesystem**: one JSON ledger file under a configurable data directory.
- No other network service, database, or third-party SDK is required for the offline path.

## 4. Components (one module per architectural element)

| Component (module) | Responsibility | Implements |
|---|---|---|
| `config.py` | Load configuration: category whitelist, budgets, endpoint, timeout, token budget; read secret from env only. | FR-001, SEC-001, COST-001 |
| `models.py` | Immutable-ish data records: `Transaction`, `Category`, `Budget`, `CategorizationResult`, `GuardrailDecision`. | FR-001, FR-002, QA-003 |
| `categorizer/base.py` | `Categorizer` interface: `categorize(transaction) -> CandidateCategory`. | FR-002, INV-004 |
| `categorizer/rule_based.py` | Deterministic keyword/rule fallback categorizer; always available offline. | FR-003, INV-005, COST-002 |
| `categorizer/llm.py` | Optional LLM categorizer; assembles prompt, calls endpoint, parses a constrained candidate; raises/degrades on failure. | FR-002, PERF-002, SEC-002 |
| `guardrail.py` | Deterministic authority layer: whitelist check, amount conservation, structural validation, provenance/reason recording. | INV-001, INV-002, INV-004, INV-006, QA-003, SEC-002 |
| `budget.py` | `BudgetPolicy`: exact-decimal accumulation and over/under-budget decisions; the only authority on compliance. | FR-004, INV-003 |
| `ledger.py` | Persistence: serialize/deserialize ledger JSON; round-trip consistency; no secret field. | FR-005, SEC-001 |
| `prompt.py` | Prompt assembly pipeline: identity, standing constraints, retrieved rules, history, resumable state, current task; dedup/prioritize/budget/compact/re-inject. | COST-001, INV-004 |
| `eval.py` | Fixed evaluation-set replay; faithfulness, relevance, safety-escape counters; deterministic report. | FR-006, QA-001 |
| `app.py` | CLI wiring and pipeline orchestration; selects categorizer, runs guardrail then policy, records provenance. | FR-007, FR-003 |

## 5. Authority boundaries: advisory vs authoritative

This split is the central safety-relevant boundary (INV-001…006, SEC-002).

### 5.1 Advisory layer (may suggest, may not decide)
- `categorizer/llm.py` and any model output.
- Produces a **candidate** (category label, optional label). It has no handle on budgets,
  ledger mutation, deletion, or tool invocation.
- Model text is parsed into a narrow candidate object; raw model strings never reach
  evaluators, shell, or mutating APIs (SEC-002).

### 5.2 Authoritative layer (deterministic code decides)
- `guardrail.py` accepts or rejects the candidate against the closed whitelist and schema.
- `budget.py` owns every compliance/over-budget decision using exact decimal arithmetic.
- `ledger.py` owns persistence.
- The advisory layer cannot write a budget, flip a compliance flag, or bypass the guardrail.

### 5.3 Boundary enforcement points
1. Candidate enters the system only through the guardrail's typed validation entry point.
2. Category is resolved to the whitelist; an out-of-whitelist candidate is rejected and
   replaced with `other` (INV-001).
3. Amount on the record is copied from the input transaction; any model-supplied amount
   field is discarded (INV-002).
4. Compliance status is computed solely by `BudgetPolicy` after guardrail acceptance (INV-003).

## 6. AI component design (layered context & assembly)

### 6.1 Layered context the model receives each turn
1. **Identity**: role and limited task description (categorize one transaction description).
2. **Standing constraints** (always injected, never dropped by compaction): closed
   whitelist, single label, output schema, no amounts, no privileged actions.
3. **Retrieved knowledge**: whitelist definitions and keyword examples from configuration.
4. **Conversation history**: recent prior turns for the same session, truncated by budget.
5. **Resumable state**: current ledger month and pending record id (read-only context).
6. **Current task**: the single transaction description to categorize.

### 6.2 Assembly pipeline
`dedup → prioritize → budget → compact → assemble → validate`
- **Dedup**: remove duplicate constraint/rule entries.
- **Prioritize**: standing constraints > whitelist definitions > current task > history.
- **Budget**: cap at token-equivalent budget (default 600; COST-001).
- **Compact**: when over threshold, truncate history first, then examples; preserve constraints.
- **Re-inject**: after any compaction, the standing constraints and whitelist are re-injected
  verbatim so critical rules are never lost (ADR-001, COST-001).
- **Validate**: assembled prompt size re-checked against budget before sending.

### 6.3 Token budget and compaction threshold
- Hard cap: 600 token-equivalent units per assembled prompt (configurable).
- Compaction triggers at 80% of cap (480 units); standing constraints and whitelist are
  exempt from truncation.
- Timeout for the LLM call: 8 s hard limit (PERF-002); timeout/error degrades to fallback.

## 7. Agent workflow (human-supervised)

1. **Plan gate**: agent reads `AGENTS.md` → this blueprint → relevant ADRs/invariants;
   produces an execution plan (traceability, interface contract, scope, test strategy,
   steps) and **stops for human approval before code** (D9, Prompt.md).
2. **Build stage**: after approval, agent implements one module at a time against its
   contract; each stage stops for human review.
3. **Verify stage**: offline deterministic tests run; guardrail/invariant tests must fail
   if the invariant is violated; full historical suite must stay green (regression gate).
4. **Revise stage**: test evidence drives any architecture revision, recorded as an ADR
   update and a review memo; safety-critical changes require human approval (GOV-003).

## 8. Permissions (summary; full model in `docs/architecture/permission-model.md`)
- Default: no read, no write. Every path is an explicit whitelist per agent role.
- The coding agent may read governance/architecture/requirements and `src/`; it may write
  only its assigned module and its tests; guardrail/budget/permission modules are frozen
  unless an ADR + human approval is recorded.
- Secrets are never read by the agent from the repository; the key lives only in the environment.

## 9. Verification strategy (three tiers; see D4)
- **Structural**: imports resolve; module boundaries respected; permissions/API surface
  checked; fitness functions confirm one-module-per-element.
- **Regression**: every change runs the full historical offline suite; any regression blocks.
- **Behavioral**: fixed eval set meets faithfulness/relevance thresholds with zero safety
  escapes; live tests are isolated and skipped without a key.

## 10. Observability
- Per-record provenance: source (`llm` / `rule` / `fallback`), guardrail decision, reason code.
- Evaluation report: faithfulness, relevance, safety-escape count, per-category counts.
- Logs redact any secret (SEC-001); logs contain no raw key.
- AI-use log records every code/prompt change and human intervention (GOV-002).

## 11. Change policy
- Requirements change → update registry + schema + trace matrix within one sprint (context
  freshness, `.agent/rules.md`).
- Safety-critical paths (`guardrail.py`, `budget.py`, permission model): change requires an
  ADR entry and an approving review memo before merge (GOV-003).
- New work **extends** the existing baseline; it never replaces an established module or
  its contract (structural constraints, D3).
- Any prompt/model change must replay the fixed eval set and meet thresholds before it
  reaches the default path (semantic evaluation gate, CI gate 4).
- Reopen conditions for the chosen architecture are listed in ADR-001.
