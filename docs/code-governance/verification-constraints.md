# Verification Constraints (D4)

Rules the verification agent applies to every change.

## 1. Coverage obligations
- **Every fit criterion** in `requirements.yaml` has at least one test that exercises it.
- **Every invariant** in `invariants.md` has at least one test that **fails when the invariant
  is violated** (mutation-style: break the rule and the test goes red).
- **Every test** references the requirement or invariant it verifies, in its docstring or a
  `# verifies:` comment, matching the trace matrix.
- Every new feature ships at least one negative test (invalid/adversarial input → safe rejection
  or fallback).

## 2. Three-tier verification

### Tier 1 — Structural
- Imports resolve; no cyclic imports; module-to-element mapping holds (one element, one module).
- Permission/API-surface checks: the model-facing package exports no budget-write, ledger-delete,
  shell, or tool-call method.
- Fitness functions confirm the advisory/authority boundary and frozen-path separation.
- Requirements registry validates against its JSON schema (schema gate).

### Tier 2 — Regression
- Every change runs the **full historical offline suite**; any regression blocks merge.
- Tests are independent (no shared mutable state, own fixtures/temp dirs, order-insensitive).
- Live tests do not gate the offline suite; they skip cleanly without a key.

### Tier 3 — Behavioral
- Fixed evaluation set replays; thresholds:
  - **Faithfulness**: accepted candidate matches the expected label where one is annotated.
  - **Relevance**: accepted candidate is a plausible whitelist label for the description.
  - **Safety escapes**: any whitelist/amount/compliance boundary bypass = **0** (zero tolerance).
- A prompt or model change must replay the fixed set and meet thresholds before reaching the
  default path (semantic evaluation gate).

## 3. Gate mapping (CI)
| Gate | Tier | Check |
|---|---|---|
| Test approval gate | Process | Tests for a change are approved before implementation begins. |
| Static analysis gate | Structural | Lint, type/import check, dependency check; contract/security/API-surface/permission checks on safety-path PRs. |
| Schema gate | Structural | Registry validates against `req-schema.json`. |
| Semantic evaluation gate | Behavioral | Fixed-set replay meets faithfulness/relevance/safety thresholds after prompt/model change. |
| Regression gate | Regression | Full prior suites pass; no regression. |
| AI-use log gate | Process | src/prompt change accompanies an ai-use-log update. |

## 4. Evidence standards
- A review records: spec alignment, architecture alignment, code/test quality, security and
  efficiency checks, and operational metadata (suite run, counts, timing).
- Verification does not approve code it has not run; offline results must be reproducible from a
  clean checkout.
- Defects found during verification are entered in `bug-diary.md`; tracked cleanup in `debt-register.md`.
