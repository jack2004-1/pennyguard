# Evaluation Logbook (D2.9)

Accumulated evidence behind the architecture choices. Entries are chronological; each records
the question, the observation/measure, and the conclusion carried into the baseline.

## Entry E-01 — Does the offline path need any network or secret?
- **Question**: Can the default pipeline run deterministically without an LLM endpoint or key?
- **Evidence**: Design review of FR-003, COST-002, QA-001; the rule-based classifier covers the
  fixed whitelist with a keyword table; guardrail and policy are pure deterministic code.
- **Conclusion**: Default configuration builds no LLM client; offline tests never touch the network.
  Live LLM behavior is isolated under `test/live/` and skipped without a key.

## Entry E-02 — Where should the safety boundary sit?
- **Question**: At which layer can unsafe model output be blocked with enforceable code?
- **Evidence**: INV-001…006 require whitelist, amount conservation, structural validation, and
  deterministic compliance. A model-direct path cannot guarantee these; a separate guardrail
  module can, and each rule has a failing-test counterpart.
- **Conclusion**: Guardrail accepts/rejects candidates; `BudgetPolicy` owns compliance; the
  model-facing package has no budget-write surface (INV-006).

## Entry E-03 — Is a retrieval layer warranted for the label set?
- **Question**: Would RAG over a local corpus improve categorization for this baseline?
- **Evidence**: The whitelist is small and closed (8 labels); descriptions are short merchant
  memos. Keyword rules plus an optional LLM cover the set; an index adds storage and
  non-determinism without a measured recall gap.
- **Conclusion**: RAG deferred; tracked in the option ledger with a reopen trigger tied to recall.

## Entry E-04 — Prompt cost and compaction behavior
- **Question**: How is per-call LLM cost bounded, and are critical constraints preserved after compaction?
- **Evidence**: COST-001 sets a 600-unit cap with an 80% compaction threshold; standing
  constraints and whitelist are exempt from truncation and re-injected after compaction.
- **Conclusion**: Assembly pipeline `dedup → prioritize → budget → compact → assemble → validate`;
  budget compliance is checked before sending (RP-10).

## Entry E-05 — Evaluation thresholds
- **Question**: What quality thresholds gate a prompt/model change?
- **Evidence**: Fixed offline fixture set; metrics are faithfulness (candidate matches expected
  label where a label is known), relevance (accepted candidate is a plausible whitelist label),
  and safety escapes (any whitelist/amount/compliance boundary bypass), which must be zero.
- **Conclusion**: Semantic evaluation gate replays the fixed set; any threshold failure blocks
  the change (CI gate 4). Thresholds are recorded in `eval.py` and the verification constraints.

## Open evidence to collect later
- Real merchant-memo sample coverage for the rule fallback (evaluation debt, see debt register).
- Latency distribution once a live model is wired (PERF-001 measured offline only at baseline).
