# Structural Constraints (D3)

Module organization rules that keep the codebase aligned with the architecture.

## 1. One element, one module
- Every architectural element in blueprint §4 maps to exactly one module under `src/pennyguard/`.
- No architectural element is split across multiple modules; no module hosts two unrelated
  architectural elements. If a module grows two responsibilities, split it and record an ADR.
- Module names match the trace-matrix component names; tests are named to match their module.

## 2. Extend the baseline, do not replace it
- New work adds modules, functions, or optional implementations behind an existing interface.
- Do not rewrite an established module or change its public signature without an ADR and human
  approval; a contract change is a breaking change and must be co-versioned with its tests.
- Deprecation, not silent deletion, is the default for removed behavior.

## 3. Traceability in code
- Each module header cites the ADR and the requirement/invariant IDs it implements
  (QA-002). Non-trivial functions cite the specific invariant or requirement they enforce.
- Example header:
  ```
  # Module: guardrail.py
  # ADR: ADR-001
  # Implements: INV-001, INV-002, INV-004, INV-006, QA-003, SEC-002
  ```
- A function that enforces an invariant references that invariant ID in its docstring.

## 4. Authority boundaries (structural)
- **Advisory package**: `categorizer/` may produce candidates only. It must not import
  `budget.py` mutators, ledger write APIs, or any shell/exec path.
- **Authority layer**: `guardrail.py` accepts/rejects candidates; `budget.py` owns compliance;
  `ledger.py` owns persistence. These are frozen paths.
- Dependency direction is inward: `app.py` → categorizer/guardrail/budget/ledger; lower layers
  must not import higher layers. No cyclic imports between modules.
- Model output crosses the boundary only as a validated candidate object; raw model strings do
  not reach evaluators, shell, or mutating APIs (SEC-002).

## 5. Package and file rules
- Shared records and enums live in `models.py`; no duplicated class/type definitions.
- Configuration constants and the whitelist are sourced from `config.py`, not scattered literals.
- Runtime secrets are read from environment variables in `config.py`; no secret literal anywhere.
- Third-party dependencies are declared explicitly; no transitive-only imports assumed.

## 6. Fitness checks (CI structural tier)
- Import resolution and no-cyclic-import check run on every commit.
- API-surface check confirms the model-facing package exports no budget/ledger write method.
- Module-to-element mapping is checked against the trace matrix in review.
