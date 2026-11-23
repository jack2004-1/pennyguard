# Project Covenant (.agent/rules.md, D3)

The binding contract between the human owner and any AI agent working on PennyGuard.

## 1. Abstraction limits
- The `Categorizer` interface is the sole classification contract; implementations conform to
  it and are swappable behind it.
- The advisory layer (`categorizer/`) exposes candidates only; it must not reach into
  authority-layer decisions (guardrail acceptance, budget compliance, persistence).
- Boundaries between modules are crossed through typed records in `models.py`, not shared
  internal state.

## 2. Dependency constraints
- Dependency direction: `app.py` → {categorizer, guardrail, budget, ledger, prompt, eval, config}.
  Lower layers never import higher layers; no cyclic imports.
- Standard library preferred; any third-party runtime dependency must be declared in
  `requirements.txt` and justified in the debt register if it adds risk.
- No provider SDK lock-in; the LLM client isolates provider specifics behind the interface.
- No dependency on network or secret in the offline test path.

## 3. Test independence
- Every feature has at least one **negative test** that exercises an invalid or adversarial
  input and asserts safe rejection/fallback.
- Tests are independent: order does not matter; no shared mutable state between tests; each
  test builds its own fixtures and temporary data dir.
- Every test references the requirement or invariant it verifies (verification constraints).
- Offline and live tests are separated; live tests skip cleanly without a key.

## 4. Safety-critical change control
- Safety-critical code: `guardrail.py`, `budget.py`, the permission model, and any boundary
  check. Changing it requires: (a) an ADR entry describing the decision and reopen
  conditions, and (b) explicit human approval recorded in a review memo.
- A safety-critical change without these two records is rejected at review regardless of tests.

## 5. Context freshness
- When a requirement changes, the registry, schema, trace matrix, invariants, and this covenant
  are updated within one sprint, in the same change where practical.
- Rules and architecture artifacts are reviewed after each requirement or defect change;
  stale rules are a tracked debt, not accepted drift.

## 6. Contract on AI-generated code
- Agent-generated code is treated as unreviewed until it passes structural, regression, and
  behavioral verification and a human review memo.
- The human remains accountable for every merged decision; the agent does not self-approve.
