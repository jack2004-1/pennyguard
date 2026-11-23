# Risk List (D2.10)

Assumptions that could become defects, with their review trigger and mitigation.

| ID | Assumption / risk | Potential defect | Likelihood | Impact | Mitigation | Review trigger |
|---|---|---|---|---|---|---|
| R-01 | The keyword rule table covers common merchant memos. | Fallback mis-categorizes descriptions not in the table. | Medium | Medium | Keep fallback conservative; unknown terms map to `other`; provenance records fallback source. | Offline fixture relevance drops below threshold, or user reports recurring `other` labels. |
| R-02 | The model returns a parseable constrained payload. | Markdown-wrapped or prose response breaks parsing. | Medium | Medium | Strict structural validation degrades to fallback (INV-004); parser strips fences defensively. | Malformed-response rate rises in eval logs. |
| R-03 | Amounts parse cleanly (decimals, no thousands separators in baseline input). | Mis-parsed amount corrupts conservation check. | Low | High | Deterministic decimal parsing; invalid amounts rejected at input; amount never sourced from model. | Any input parse failure appears in logs/tests. |
| R-04 | Ledger file stays readable across versions. | Corrupt or future-version file blocks startup. | Low | Medium | RP-07/RP-08 recovery: missing/corrupt file starts empty and backs up the corrupt copy; schema version field. | Recovery event triggers in normal use. |
| R-05 | A transaction description could contain prompt-instruction text. | Model treats description text as a system instruction. | Medium | High | Description is placed only in the current-task layer; standing constraints are separate and privileged; model output still passes guardrail; no tool calls. | Eval set includes adversarial descriptions; any boundary bypass is a safety escape. |
| R-06 | Python 3.14 wheel availability for test dependencies. | Dependency install fails in a clean environment. | Low | Medium | Dependencies limited to pytest + PyYAML; CI pins versions; fallback to standard-lib where possible. | Clean-env install or CI job fails on dependency resolution. |
| R-07 | The fixed fixture set is small; thresholds may overfit to it. | Eval gate passes while real coverage is weak. | Medium | Medium | Fixture includes edge/adversarial cases; expand corpus before claiming generalizability; track evaluation debt. | Fixture coverage review at each sprint; relevance trends down. |
| R-08 | Dates are supplied as ISO `YYYY-MM-DD`. | Non-ISO date breaks record creation. | Low | Low | Input validation rejects unparseable dates; clear error exit. | Date parse failures appear in CLI errors. |
| R-09 | The LLM endpoint stays OpenAI-compatible. | Provider-specific schema breaks the client. | Low | Low | Thin client behind the `Categorizer` interface; provider adapter isolated in `llm.py`. | Endpoint contract changes; new provider required. |

## Review cadence
- Revisit this list each sprint and before any safety-critical change.
- A triggered risk that exposes a missing invariant must be added to the invariant register
  and given a failing test.
