# AGENTS.md — Coding Agent Entry Point (D3)

> This is the single entry point for any AI coding agent working on PennyGuard. Read this
> file first, then follow the reading order below. Do not start code before the human
> approves the plan produced from `Prompt.md`.

## 1. Build target
Build and maintain **PennyGuard**, a local CLI that categorizes personal-expense descriptions
with an optional LLM component behind a deterministic guardrail, and owns budget decisions in
deterministic policy code. Full scope/out-of-scope: see `architecture-blueprint.md` §1.

## 2. Reading order (mandatory)
1. `Prompt.md` — static launch instruction; produce a plan and stop for approval.
2. `architecture-blueprint.md` — master constraint document.
3. `docs/architecture/adr/001-guarded-hybrid-classifier.md` — chosen architecture and rationale.
4. `docs/architecture/invariants.md` — zero-tolerance rules and fallbacks.
5. `docs/architecture/trace-matrix.md` — requirement → component → test → monitor.
6. `docs/architecture/permission-model.md` and `.opencode/permissions.jsonc` — allowed paths.
7. `docs/code-governance/structural-constraints.md`, `verification-constraints.md`.
8. `docs/req/requirements.yaml` — machine-readable requirements and fit criteria.

## 3. Code baseline
- Language: Python 3.11+ (developed on 3.14); standard library preferred; third-party runtime
  dependencies are limited and declared in `requirements.txt`.
- Source lives in `src/pennyguard/`; deterministic offline tests in `test/offline/`;
  API-dependent tests in `test/live/`.
- Existing modules are the baseline: **extend, never replace** an established module or its
  public contract without an ADR and human approval.

## 4. Read / modify / freeze scope
### Read (allowed)
- All `docs/` governance and architecture files, `AGENTS.md`, `architecture-blueprint.md`,
  `Prompt.md`, existing `src/` and `test/`.

### Modify (only what the approved plan names)
- The single source module assigned in the plan and its paired offline test.
- `docs/ai-use-log.yaml`: append an entry for every code or prompt change (GOV-002).
- A new versioned file under `prompts/` (never edit a released prompt version in place).

### Frozen (do not modify without ADR + human approval)
- `src/pennyguard/guardrail.py`, `src/pennyguard/budget.py` — safety-critical authority layer.
- `.opencode/**`, `.agent/**` — permission and rules files, human-maintained.
- Existing released prompt versions under `prompts/`.
- Any environment secret: the agent must not read, print, or persist the API key.

## 5. Module organization and integration contracts
- One architectural element maps to exactly one module (see blueprint §4 and trace matrix).
- `Categorizer` interface (`categorizer/base.py`) is the only contract the app uses for
  classification; both rule-based and LLM implementations conform to it.
- Flow: `app.py` selects a categorizer → candidate goes to `guardrail.py` → accepted record
  goes to `budget.py` → `ledger.py` persists. The model-facing package must not import
  budget-mutating or ledger-mutating APIs.
- Data records are defined in `models.py`; modules exchange these typed records, not raw dicts
  at boundaries (internal dicts are acceptable only inside a module).
- Configuration is loaded by `config.py`; secrets come from environment variables only.

## 6. Verification the generated code must satisfy
- Every fit criterion has a test; every invariant has a test that fails when violated
  (`docs/code-governance/verification-constraints.md`).
- Each new feature ships at least one negative test.
- Offline tests are deterministic: no network, no randomness, no time dependence in assertions.
- Run the full offline suite before requesting review; zero regressions required.
- Safety-critical changes include an ADR reference and a review memo verdict.

## 7. Hard rules
- Do not invent a new budget-write, delete, shell, or tool-call path reachable from model output.
- Do not hard-code secrets, endpoints with embedded keys, or provider SDK locks.
- Cite the requirement/invariant IDs implemented in each module header and non-trivial function docstring.
- If a plan would change a frozen path or the public contract, stop and request an ADR and approval.
