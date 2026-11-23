# Always-On Behavioral Rules (D3)

Human-only file. The coding agent must follow these in every session; they are not edited by
the agent.

1. **Entry order**: Read `AGENTS.md`, then the blueprint and referenced ADR/invariants before
   proposing any change.
2. **Plan before code**: Produce an execution plan (traceability, interface contract, scope
   boundary, test strategy, steps) and stop for human approval before writing code (D9).
3. **Stay in scope**: Touch only the module and paired test named in the approved plan; do not
   refactor unrelated code "while here".
4. **Default deny permissions**: If a file or path is not on your whitelist, do not read or
   write it; ask the human instead of working around the rule.
5. **Frozen paths**: Never edit `guardrail.py`, `budget.py`, permission/rules files, or a
   released prompt version without an ADR and explicit human approval.
6. **Determinism**: Offline tests must not depend on network, the clock, randomness, or a
   secret. Live-only behavior lives under `test/live/`.
7. **No secrets**: Never read, hard-code, print, or persist the API key or any credential.
8. **Traceability**: Cite requirement/invariant IDs in module headers and invariant-enforcing
   functions; keep the trace matrix current.
9. **Tests first per change**: For each change, its tests are approved before implementation
   (test approval gate); ship at least one negative test per feature.
10. **Keep the suite green**: Run the full offline suite before review; do not merge a regression.
11. **Log AI use**: Append an `ai-use-log.yaml` entry whenever you change code or a prompt,
    including what the human approved, redirected, or rejected.
12. **No autonomous privileged actions**: Do not add budget writes, record deletion, shell
    execution, or tool-call paths reachable from model output.
13. **Honest uncertainty**: If a requirement or contract is ambiguous, stop and ask rather
    than guessing; record the ambiguity resolution in the review memo.
