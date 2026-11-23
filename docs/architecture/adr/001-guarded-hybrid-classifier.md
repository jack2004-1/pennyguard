# ADR-001: Guarded Hybrid Classifier with Deterministic Authority Layer

- **Status**: Accepted (baseline v1.0, 2026-11-23)
- **Decider**: Yiyang BU (human, solo)
- **Related requirements**: FR-002, FR-003, INV-001…006, QA-001, COST-001, PERF-002, SEC-001, SEC-002
- **Supersedes**: none (from-scratch project)

## 1. Context

PennyGuard must contain a genuine AI component that suggests budget categories from
free-text transaction descriptions, while satisfying a hard safety boundary: AI output must
be constrained by deterministic code. The baseline must run offline and deterministically for
CI and grading, must not require a secret by default, and must keep LLM cost/latency bounded.

## 2. Decision process

1. Classified requirements by authority: which decisions may be suggested by the model and
   which must be owned by deterministic code (see blueprint §5).
2. Generated candidate architectures (see `evaluation-table.md` and `option-ledger.md`):
   model-direct, rules-only, retrieval-augmented, and guarded hybrid.
3. Evaluated each against the drivers: offline determinism, enforceability of the safety
   boundary, traceability, cost, and maintainability.
4. Selected the guarded hybrid; recorded rejected options and reopen conditions below.

## 3. Chosen architecture

A **hybrid categorizer behind a deterministic guardrail**:

- A `Categorizer` interface has two implementations:
  - `RuleBasedCategorizer` — deterministic keyword/rule fallback, always available offline.
  - `LlmCategorizer` — optional OpenAI-compatible client; produces a constrained candidate.
- A `Guardrail` deterministic layer validates every candidate (whitelist, amount
  conservation, structural schema, provenance/reason).
- A `BudgetPolicy` deterministic module owns all compliance decisions.
- Selection policy: use the LLM categorizer only when endpoint + key are configured;
  otherwise use the rule-based classifier. Any LLM failure degrades to fallback (INV-005).

### 3.1 Layered context sent to the model each turn
1. **Identity**: limited role — categorize one transaction description into one whitelist label.
2. **Standing constraints** (non-trimmable): closed whitelist, single label, output schema,
   do not provide amounts, no privileged actions.
3. **Retrieved knowledge**: whitelist definitions and keyword examples from configuration.
4. **Conversation history**: recent prior turns, truncated by budget.
5. **Resumable state**: current ledger month and pending record id (read-only).
6. **Current task**: the single transaction description.

### 3.2 Assembly pipeline
`dedup → prioritize → budget → compact → assemble → validate`
- **Dedup**: collapse duplicate constraint/rule entries.
- **Prioritize**: standing constraints > whitelist definitions > current task > history.
- **Budget**: token-equivalent cap, default **600** units (COST-001).
- **Compact**: trigger at **80% (480 units)**; history is truncated first, then examples;
  standing constraints and whitelist are exempt.
- **Re-inject**: after compaction, standing constraints and the full whitelist are
  re-injected verbatim so critical constraints survive compaction.
- **Validate**: re-check assembled size against the cap before sending; reject if over.

### 3.3 Budget and timeout
- Prompt cap: 600 token-equivalent units; compaction threshold 480.
- LLM call timeout: **8 s** hard limit (PERF-002); timeout, transport error, or malformed
  payload degrades to the rule-based fallback.

## 4. Alternatives considered

| Alternative | Why rejected |
|---|---|
| **Model-direct**: model output written straight to the ledger | Fails INV-001/002/003/SEC-002: no enforceable whitelist, amount, or compliance control; non-deterministic; unsafe for an autonomous boundary. |
| **Rules-only (no AI component)** | Satisfies determinism but fails the course requirement of at least one genuine AI component (§1 Overview). |
| **Retrieval-augmented over a local corpus** | Adds index/storage complexity and non-determinism for a small closed label set; deferred until the label space grows. |
| **Separate model service over HTTP** | Over-engineered for a solo local CLI; couples the baseline to a running service. |

## 5. Consequences

### Positive
- Safety boundary is enforceable in deterministic, reviewable code; each invariant has a
  failing-test counterpart.
- Offline default keeps CI/grading independent of network and secrets; live path is isolated.
- Model is swappable behind the `Categorizer` interface; prompt and model changes are gated
  by the fixed eval set.
- Clear traceability: requirement → module → test → monitor.

### Negative / costs
- Two categorizer implementations to maintain; rule table must be kept aligned with the
  whitelist.
- Guardrail and policy modules are frozen paths requiring review to change (process overhead).
- Faithfulness depends on a small fixed fixture set; evaluation debt is tracked in the debt register.

## 6. Reopen conditions

Re-open this ADR if any of the following occurs:
- The label space grows beyond the closed whitelist or multi-label tagging becomes required.
- A second model provider or a local embedding/RAG path is needed for coverage.
- The fixed eval set shows the rule fallback cannot reach the relevance threshold on a
  realistic fixture, requiring a retrieval layer.
- Compliance decisions need shared/rolling budgets that the current per-category monthly
  policy cannot express.

## 7. Conformance checks

- `guardrail.py` is the only component that accepts/rejects a candidate.
- `budget.py` is the only component that sets compliance status.
- No model-facing module imports a ledger-mutating or budget-write API (INV-006, SEC-002).
