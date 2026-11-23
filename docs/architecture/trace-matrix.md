# Trace Matrix (D2.4)

Maps every requirement to its enforcing component, its test/evidence, and its runtime
monitor. Test paths are relative to the repo root. Offline tests run without network or key.

| Req ID | Type | Enforcing component | Test / evidence | Runtime monitor |
|---|---|---|---|---|
| FR-001 | functional | `src/pennyguard/models.py` | `test/offline/test_models.py::test_transaction_record_valid` | Record id/amount/date present on every import. |
| FR-002 | functional | `categorizer/base.py`, `guardrail.py` | `test/offline/test_categorizer.py::test_result_category_in_whitelist` | Result provenance source recorded per record. |
| FR-003 | functional | `categorizer/rule_based.py`, `categorizer/llm.py`, `app.py` | `test/offline/test_categorizer.py::test_no_key_uses_rule_classifier_no_network` | Active categorizer source in provenance; no client built without config. |
| FR-004 | functional | `budget.py` | `test/offline/test_budget.py::test_over_budget_flag_exact` | Per-category status in `status` report. |
| FR-005 | functional | `ledger.py` | `test/offline/test_ledger.py::test_roundtrip_consistent` | Ledger load/save round-trip check on startup. |
| FR-006 | functional | `eval.py` | `test/offline/test_eval.py::test_eval_report_zero_safety_escape` | Eval report faithfulness/relevance/safety_escape counters. |
| FR-007 | functional | `app.py` | `test/offline/test_app_cli.py::test_subcommands_run` | CLI exit codes and structured output. |
| INV-001 | invariant | `guardrail.py` | `test/offline/test_guardrail.py::test_out_of_whitelist_rejected` | Reason code `NOT_IN_WHITELIST` in provenance. |
| INV-002 | invariant | `guardrail.py` | `test/offline/test_guardrail.py::test_amount_conservation` | Provenance flag `amount_override_ignored`. |
| INV-003 | invariant | `budget.py` | `test/offline/test_budget.py::test_ai_cannot_flip_compliance` | Status recomputed by policy; `compliance_override_rejected` event. |
| INV-004 | invariant | `guardrail.py` | `test/offline/test_guardrail.py::test_malformed_response_degraded` | Reason code `MALFORMED_RESPONSE`; source `fallback`. |
| INV-005 | invariant | `categorizer/llm.py`, `app.py` | `test/offline/test_degradation.py::test_llm_failure_modes_degrade_cleanly` | Degradation event + redacted failure message. |
| INV-006 | invariant | Package boundary (`categorizer/` vs `budget.py`) | `test/offline/test_guardrail.py::test_no_ai_budget_write_surface` | Boundary-violation security event. |
| QA-001 | quality | `eval.py`, `app.py` | `test/offline/test_eval.py::test_replay_deterministic` | Replay diff empty across consecutive runs. |
| QA-002 | quality | All modules (header citations) | This matrix + module header requirement/invariant IDs | Structural fitness check in CI. |
| QA-003 | quality | `guardrail.py`, `models.py` | `test/offline/test_guardrail.py::test_provenance_and_reason_recorded` | Provenance + reason code present on every result. |
| PERF-001 | performance | `app.py`, `categorizer/*`, `guardrail.py` | `test/offline/test_perf.py::test_offline_p95_under_threshold` | p95 latency recorded in perf test report. |
| PERF-002 | performance | `categorizer/llm.py` | `test/offline/test_degradation.py::test_llm_timeout_degrades` | Timeout event; fallback source recorded. |
| COST-001 | cost | `prompt.py` | `test/offline/test_prompt_assembly.py::test_prompt_within_budget` | Assembled prompt size vs budget in eval report. |
| COST-002 | cost | `categorizer/llm.py` | `test/offline/test_categorizer.py::test_no_client_without_config` | Zero LLM client construction in default config. |
| GOV-001 | governance | `scripts/validate_requirements.py` | CI `schema-gate`; `docs/req/requirements.yaml` vs `req-schema.json` | Registry validation result in CI run. |
| GOV-002 | governance | `docs/ai-use-log.yaml` | CI `ai-use-log-gate` (src/prompt change requires log update) | Log freshness check in CI. |
| GOV-003 | governance | Review process; `docs/review-memo.md` | Review memo per change; ADR reference for critical paths | Review verdict recorded per PR. |
| SEC-001 | security | `config.py`, `ledger.py`, logging | `test/offline/test_security.py::test_secret_not_persisted_or_leaked` | Secret redaction check over persisted/log strings. |
| SEC-002 | security | `guardrail.py`, package boundary | `test/offline/test_security.py::test_model_output_not_executed` | No model-originated string reaches mutating/eval/shell path. |

## Coverage rule
Every requirement above has at least one offline test or a named governance artifact. If a
new requirement is added, its row and test must land in the same change (context freshness).
