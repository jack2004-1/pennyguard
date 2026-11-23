# Technical Debt Register (D4)

Debt is tracked by the AI-era categories below. Status: Open | Mitigated | Closed.
New entries are added when a shortcut, gap, or agent-generated weakness is accepted knowingly.

| ID | Category | Description | Source / how introduced | Mitigation | Status |
|---|---|---|---|---|---|
| TD-01 | Prompt rot | Prompt v1.0 may drift from the whitelist or schema as rules evolve; no automated prompt-regression yet beyond the fixed eval set. | Baseline prompt authored early; rules may change later. | Version prompts under `prompts/`; replay fixed eval set on each change; review prompt against invariants each sprint. | Open |
| TD-02 | Hallucinated dependencies | Agent may propose packages/APIs that do not exist or are unnecessary. | Agent code generation. | Keep dependencies declared and minimal; offline tests import only declared modules; review imports in each memo. | Mitigated |
| TD-03 | Untouchable code | Frozen authority modules (`guardrail.py`, `budget.py`) may become hard to modify if tests and docs lag. | Safety-critical freeze. | Keep invariant tests and trace citations tight; any change requires ADR + approval; document rationale in code headers. | Open |
| TD-04 | Hidden dependencies | LLM provider quirks or endpoint behavior may be assumed implicitly rather than declared. | Optional live path. | Isolate provider specifics in `llm.py`; declare OpenAI-compatible contract in ADR; live tests cover adapter seam. | Open |
| TD-05 | Agent-induced bloat | Agent may add unused modules, helpers, or abstraction "just in case". | Agent code generation. | Structural one-element-one-module rule; lint for unused exports; review removes dead code before merge. | Mitigated |
| TD-06 | Evaluation debt | The fixed fixture set is small and may not cover real merchant-memo variety; thresholds may overfit. | Baseline scope constraint. | Include edge/adversarial cases now; expand corpus before generalizability claims; log coverage gaps in logbook. | Open |
| TD-07 | Guardrail debt | New categories or output fields could arrive without a matching guardrail check. | Scope evolution. | Require an invariant + failing test whenever a new accepted output field/category is added. | Open |
| TD-08 | Human / cognitive debt | Solo author carries all roles; context may be lost between sessions; rules may drift from requirements. | Solo submission model. | Maintain trace matrix, review memos, and ai-use log; re-read blueprint at each session; context-freshness rule in `.agent/rules.md`. | Open |

## Review cadence
- Re-scan this register each sprint and after any safety-critical change.
- Closed debt must have evidence (test, memo, or cleanup commit) linked.
