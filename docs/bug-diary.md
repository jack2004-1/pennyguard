# Bug Diary (D4)

One entry per significant bug: symptom, reproduction, classification, root cause, fix, and the
invariant gap it exposed.

## Template
```
### BUG-<nnn> — <short title>
- Date: <YYYY-MM-DD>
- Symptom: <observed failure>
- Reproduction: <steps / command>
- Classification: <config/parsing/guardrail/boundary/performance/security/...>
- Root cause: <why it happened>
- Fix: <change made>
- Invariant gap exposed: <which invariant/check was missing or weak, if any>
- Prevention: <test or rule added to stop recurrence>
```

---

### BUG-001 — Requirements YAML failed to parse on a bare-scalar colon
- Date: 2026-11-23
- Symptom: `yaml.safe_load` raised `ScannerError: mapping values are not allowed here` at
  QA-001 statement line.
- Reproduction: Run `scripts/validate_requirements.py` against the initial registry.
- Classification: Parsing / configuration format.
- Root cause: A free-text statement contained an inline colon followed by a space
  (`deterministic: repeated...`) inside an unquoted plain scalar, which YAML read as a mapping.
- Fix: Convert that field to a folded block scalar (`>-`); scan other long-text fields for the
  same pattern.
- Invariant gap exposed: No parse-level check existed before the schema gate ran; registry
  validity was assumed from authoring rather than verified.
- Prevention: Schema gate runs a YAML load before schema validation; registry must parse cleanly
  in CI before any structural check.

### BUG-002 — `group` registry field validated as integer against a string schema
- Date: 2026-11-23
- Symptom: Schema gate failed with `$.meta.group: expected string, got int`.
- Reproduction: Run `scripts/validate_requirements.py` after BUG-001 fix.
- Classification: Schema / data typing.
- Root cause: `group: 43` was written as an unquoted numeric-looking scalar; YAML coerced it to
  int, conflicting with the schema's string type and pattern.
- Fix: Quote the value (`group: "43"`); confirm `student_id` is similarly quoted.
- Invariant gap exposed: Typing of identifier-like registry fields was not asserted during authoring.
- Prevention: Schema gate enforces type/pattern; identifier fields are authored as quoted strings.

### BUG-003 — Unmatched bracket in ledger deserializer
- Date: 2026-11-23
- Symptom: Test collection failed with `SyntaxError: unmatched ')'` in `ledger.py` while
  constructing `CategorizationResult` in the deserializer.
- Reproduction: Collect the offline suite before the fix; Python refuses to import the ledger module.
- Classification: Syntax / deserialization structure.
- Root cause: An extra closing parenthesis remained after the `records.append(...)` block.
- Fix: Removed the unmatched bracket; deserializer bracket balance verified by collection and
  round-trip test.
- Invariant gap exposed: No import/collection-level check ran before behavioral testing; a syntax
  error blocked the whole suite rather than surfacing as a focused failure.
- Prevention: Compile/import check runs in the static-analysis gate before the regression suite.

### BUG-004 — Native adapter exceptions bypassed the degradation contract
- Date: 2026-11-23
- Symptom: Timeout and transport-error fake clients raised raw `TimeoutError`/`ConnectionError`,
  which escaped the LLM categorizer instead of becoming a `CategorizerError` the app could degrade on.
- Reproduction: `test_llm_timeout_degrades`, `test_llm_transport_error_degrades` raised the native
  exception instead of the expected categorizer error.
- Classification: Error-handling / boundary contract.
- Root cause: Only the built-in urllib client mapped failures; the injected-client path and the
  generic call site did not convert unexpected adapter exceptions.
- Fix: Wrap the client call so any non-`CategorizerError` exception is converted to
  `CategorizerError`; unified the app's injected and self-built categorizer paths through one
  guarded `_produce_candidate` fallback.
- Invariant gap exposed: INV-005 relied on every failure mode degrading cleanly, but the conversion
  boundary was incomplete for injected adapters.
- Prevention: Degradation tests cover timeout, transport error, and raising-categorizer modes; the
  structural gate reviews the fallback path.

### BUG-005 — CLI unknown-command contract modeled as a return value
- Date: 2026-11-23
- Symptom: The unknown-command test expected `main()` to return exit code 2, but argparse calls
  `sys.exit(2)`, raising `SystemExit`.
- Reproduction: Run `test_unknown_command_returns_error` against the argparse-based parser.
- Classification: Test-contract mismatch (not a product defect in CLI behavior).
- Root cause: The test modeled the CLI error path as a function return rather than a process exit.
- Fix: Test now asserts `SystemExit` with code 2; product behavior (non-zero exit on unknown command)
  is unchanged.
- Invariant gap exposed: CLI exit semantics were not specified in the requirement's fit criterion.
- Prevention: CLI behavior is covered by a dedicated offline test; exit-code expectations are stated
  in FR-007.
