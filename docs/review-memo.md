# Review Memos (D4)

One memo per change/PR. Verdict: **APPROVE**, **CHANGES REQUIRED**, or **REJECT**. Every memo
checks spec alignment, architecture alignment, code/test quality, security, and efficiency,
and records operational metadata.

## Memo template
```
### MEMO-<nnn> — <change title>
- Change / PR: <branch or change id>
- Author: Yiyang BU
- Reviewer: Yiyang BU (human, solo; agent output reviewed)
- Date: <YYYY-MM-DD>
- Scope: <files/modules touched>
- Spec alignment: <requirements/invariants addressed; fit criteria mapped>
- Architecture alignment: <ADR/blueprint conformance; boundary respected>
- Code & test quality: <clarity, traceability citations, negative tests, independence>
- Security: <secrets, boundary/API surface, model-output isolation>
- Efficiency: <latency/cost, no redundant work>
- Operational metadata: <suite command, tests pass/fail, timing, environment>
- Issues found: <list>
- Verdict: APPROVE | CHANGES REQUIRED | REJECT
```

---

### MEMO-001 — Requirements registry and architecture baseline
- Change / PR: `baseline/requirements-architecture`
- Author: Yiyang BU
- Reviewer: Yiyang BU (human)
- Date: 2026-11-23
- Scope: `docs/req/requirements.yaml`, `req-schema.json`, `docs/architecture/**`, blueprint, ADR-001.
- Spec alignment: 25 requirements covering functional, invariant, quality, performance, cost,
  governance, security; each has a machine-checkable fit criterion and MoSCoW priority with
  explicit tradeoff. Verified against spec §3 D1.
- Architecture alignment: Guarded hybrid chosen per ADR-001; advisory/authority split matches
  blueprint §5; one element per module mapped in the trace matrix.
- Code & test quality: No source yet; test names and mappings fixed in the trace matrix; each
  invariant has a designated failing-test counterpart.
- Security: Secret limited to env var; model-facing surface defined as candidate-only; no secret
  in any artifact reviewed.
- Efficiency: Offline-first design; optional LLM path isolated; prompt budget and timeout defined.
- Operational metadata: `scripts/validate_requirements.py` → SCHEMA GATE PASSED, 25 requirements;
  local Python 3.14.7, pytest 9.2.0, PyYAML 6.0.4.
- Issues found:
  1. YAML bare-scalar colon in QA-001 statement broke parsing — fixed to block scalar.
  2. `group` parsed as integer — quoted as string to satisfy schema.
- Verdict: **APPROVE** (baseline documents approved; source implementation proceeds under plan gate).

---

### MEMO-002 — Source implementation, tests, and CI gates
- Change / PR: `baseline/implementation`
- Author: Yiyang BU
- Reviewer: Yiyang BU (human)
- Date: 2026-11-23
- Scope: `src/pennyguard/**`, `test/offline/**`, `test/live/**`, `prompts/`, `scripts/`, `.github/workflows/ci.yml`.
- Spec alignment: All 25 requirements mapped to modules and tests in the trace matrix; six
  invariants each have a failing-test counterpart; offline/live tests separated.
- Architecture alignment: Guarded hybrid per ADR-001; advisory `categorizer/` has no budget/ledger
  write surface; guardrail and budget policy remain frozen authority modules; prompt budget and
  compaction re-injection match ADR-001 §6.
- Code & test quality: One element per module; requirement/invariant IDs cited in headers; tests
  independent with own fixtures and temp dirs; negative tests for invalid amounts, bad dates,
  out-of-whitelist candidates, malformed payloads, unknown CLI command, and adversarial text.
- Security: Secret read from env only; redaction verified against result and persisted ledger;
  model output parsed into a constrained candidate; no shell/eval/mutating path reachable from model text.
- Efficiency: Offline p95 categorize+guardrail under 50 ms; no LLM client constructed in default config.
- Operational metadata: `pytest test/` → 37 passed, 1 skipped (live, no key); schema gate 25
  requirements valid; structural gate boundary intact; eval replay faithfulness 1.0, relevance 1.0,
  safety escapes 0. Local Python 3.14.7, pytest 9.2.0, PyYAML 6.0.4.
- Issues found:
  1. Unmatched bracket in ledger deserializer (collection SyntaxError) — fixed (BUG-003).
  2. Native adapter exceptions bypassed degradation — converted to `CategorizerError` uniformly (BUG-004).
  3. CLI unknown-command path raises `SystemExit`; test corrected to assert exit code 2 (BUG-005).
  4. Rule lexicon missed `amzn/mktpl` synonyms — added to fallback lexicon; guardrail kept strict.
- Verdict: **APPROVE**
