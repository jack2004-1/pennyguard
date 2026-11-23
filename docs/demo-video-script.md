# Demo Video Script — PennyGuard (assignment 327885)

- **Student**: Yiyang BU (卜毅扬), Student ID 60392800, Group 43 (solo)
- **Target**: one `.mp4`, **≤ 10 minutes**. Three required blocks (discussion 646809):
  1. Product demo — before/after behaviour comparison;
  2. Original software-engineering ideas (a plain business need does not count);
  3. Traceability + agent governance and supervision.
- **Recording rules**: do **not** show or read any API key, endpoint secret, or `.env` value;
  keep the offline default path on camera; live LLM path is described, not required on camera.
- **Environment before recording**: `Set-Location` to the project root; use
  `.venv\Scripts\python.exe`; set `$env:PYTHONPATH="src"`. Clear any old `.pennyguard/` ledger
  before the demo so the recorded `list` and `status` start empty.

## Time budget (total 09:30, leave 30 s margin)

| Segment | Time | Required block |
|---|---|---|
| 0. Opening and identity | 0:00–0:40 | Setup |
| 1. Product demo: offline happy path | 0:40–2:30 | Block 1 |
| 2. Before/after: the safety boundary in action | 2:30–4:00 | Block 1 |
| 3. Original SE ideas | 4:00–6:10 | Block 2 |
| 4. Traceability: requirement → component → test → monitor | 6:10–7:40 | Block 3 |
| 5. Agent governance and human supervision | 7:40–9:00 | Block 3 |
| 6. Debt, risks, closing | 9:00–9:30 | Wrap-up |

---

## 0. Opening and identity (0:00–0:40)

**On screen**: project root in VS Code; `README.md` open.

**Say**:
> "Hello, this is Yiyang BU, student ID 60392800, Group 43, solo submission for CS5351. The
> project is PennyGuard: a local command-line expense tool that uses an AI component to suggest a
> budget category, while deterministic code constrains every AI output. It was built from scratch;
> no code, naming, or document was reused from any prior group repository."

**Point to**: README header, author/ID/group line, the advisory/authority one-paragraph summary.

**Note (中文)**: 开场先报身份、学号、组别、单人提交；一句话讲清选题与"AI 建议 + 确定性护栏"双要求。

## 1. Product demo — offline happy path (0:40–2:30)

**On screen**: terminal at project root.

**Commands to run (offline, no key, no network)**:
```powershell
$env:PYTHONPATH = "src"
.venv\Scripts\python.exe -m pennyguard.app add --description "Coffee and toast" --amount 12.50 --date 2026-11-23
.venv\Scripts\python.exe -m pennyguard.app add --description "MTR ticket" --amount 6.00 --date 2026-11-23
.venv\Scripts\python.exe -m pennyguard.app add --description "AMZN MKTPL ORDER" --amount 39.90 --date 2026-11-23
.venv\Scripts\python.exe -m pennyguard.app list
.venv\Scripts\python.exe -m pennyguard.app status
.venv\Scripts\python.exe -m pennyguard.app eval
```

**Say**:
> "The default path runs fully offline. With no API key configured, the system selects the
> deterministic rule-based fallback and constructs no LLM client. Each record shows its category,
> its provenance source, and the guardrail reason code. The `status` command accumulates spending
> per category using exact decimal arithmetic. The `eval` command replays the fixed ten-fixture
> set and reports faithfulness, relevance, and a zero safety-escape count."

**Point to**: the `[rule]` source tag and `(OK)` reason code on each `add` line; the `status`
within_budget rows; the eval report dict with `safety_escape_count: 0`.

**Note (中文)**: 演示三条入账（food / transport / shopping），再 list、status、eval；强调默认离线、无 key、零 LLM 调用。

## 2. Before/after — the safety boundary in action (2:30–4:00)

**On screen**: `src/pennyguard/guardrail.py` and `docs/architecture/invariants.md` side by side.

**Say (before — what an unguarded model path would allow)**:
> "Without a deterministic boundary, an advisory model could return a category outside the intended
> list, propose a different amount, or mark an over-budget record as compliant. Those are exactly
> the failures this project blocks."

**Say (after — what the guarded hybrid does)**:
> "PennyGuard splits an advisory layer from an authority layer. The model-facing categorizer produces
> a candidate only. The deterministic guardrail runs four checks: structural validation, whitelist
> closure, amount conservation, and then the budget policy alone decides compliance. An
> out-of-whitelist label is rejected and replaced with the reserved `other`; any model-supplied amount
> is discarded and the input amount is kept; a model compliance signal cannot flip an over-budget
> flag."

**Point to in code**:
- `validate_candidate` — `NOT_IN_WHITELIST`, `MALFORMED_RESPONSE`, `AMOUNT_OVERRIDE_IGNORED` reason codes.
- `check_amount_conservation` — stored amount equals input amount.
- `budget.py` — `BudgetPolicy.evaluate` owns the status; the model-facing package has no budget-write surface.

**Show evidence**: open `test/offline/test_guardrail.py` and `test/offline/test_budget.py`; name the
negative tests: out-of-whitelist rejection, amount conservation, malformed-response degradation,
compliance-override rejection.

**Note (中文)**: 这是"前后对比"核心：先讲无护栏时模型可能越界改类目/金额/合规，再讲四道确定性检查如何逐一拦截；配对应负面测试作证。

## 3. Original software-engineering ideas (4:00–6:10)

**On screen**: `docs/architecture/adr/001-guarded-hybrid-classifier.md`, `evaluation-table.md`,
`prompt.py`, `runtime-policy-catalog.md`.

**Say**:
> "The business need — sorting expenses — is not the contribution. The engineering contribution is
> how the AI component is constrained and made maintainable and auditable."

Cover four SE ideas, each tied to an artifact:

1. **Advisory/authority split with a closed API surface.** The `Categorizer` interface is the only
   contract the app uses; both rule-based and LLM implementations conform to it. The model-facing
   package cannot import budget-mutating or ledger-mutating APIs; a structural test enumerates its
   exported names and confirms no write, delete, shell, or tool-call method exists.
2. **Weighted architecture selection.** Five candidates were scored against six drivers weighted by
   course priorities: safety boundary 0.25, offline determinism 0.20, genuine AI 0.15, cost/latency
   0.15, maintainability 0.12, traceability 0.13. The guarded hybrid scored 4.55; model-direct write
   scored 2.30 and fails the boundary; rules-only scores 4.10 but lacks the AI component.
3. **Bounded, layered prompt assembly.** The context is split into identity, standing constraints,
   whitelist knowledge, history, resumable state, and current task. The pipeline runs
   dedup → prioritize → budget → compact → assemble → validate under a 600-unit cap with a 480-unit
   compaction threshold. Constraints and the whitelist are exempt from truncation and re-injected
   verbatim after compaction; the LLM call has an 8-second hard timeout.
4. **Deterministic runtime policy catalog.** Fourteen degraded paths each have a concrete action:
   no key, timeout, transport error, malformed payload, out-of-whitelist label, ignored model amount,
   missing/corrupt ledger, missing budget, over-budget prompt, empty eval set, unknown CLI command,
   boundary violation, and secret redaction. Fallbacks are observable through stable reason codes.

**Point to**: evaluation-table scores; `_STANDING_CONSTRAINTS` and the assembler stages in `prompt.py`;
the RP-01…RP-14 rows in the policy catalog.

**Note (中文)**: 强调"业务需求不算原创点"，原创点是：分层权威边界、加权选型、分层上下文与压缩再注入、确定性降级策略目录。

## 4. Traceability: requirement → component → test → monitor (6:10–7:40)

**On screen**: `docs/req/requirements.yaml`, `docs/architecture/trace-matrix.md`,
`docs/architecture/invariants.md`.

**Say**:
> "Every requirement is machine-readable and maps to an enforcing component, a test or evidence
> artifact, and a runtime monitor. The registry has 25 requirements across seven types: functional,
> invariant, quality, performance, cost, governance, security. Six are zero-tolerance invariants,
> each with a test that fails when the invariant is violated."

Walk three chains on camera:
- **INV-001** closed whitelist → `guardrail.py` → `test_out_of_whitelist_rejected` → monitor reason
  `NOT_IN_WHITELIST`.
- **INV-003** deterministic compliance → `budget.py` → `test_ai_cannot_flip_compliance` → monitor
  `compliance_override_rejected`.
- **SEC-001** secret non-persistence → `config.py`/`ledger.py`/redaction →
  `test_secret_not_persisted_or_leaked` → monitor `secret_redacted`.

**Show**: the trace-matrix table rows; module headers that cite requirement/invariant IDs; the
offline suite result — 37 passed, 1 live skipped without a key.

**Run (optional, fast)**:
```powershell
.venv\Scripts\python.exe -m pytest test/offline/ -v
```
Use `-v` so the ending banner `37 passed` is clearly visible on camera. The default `-q`
quiet mode can leave the summary line buffered in the VS Code terminal; if only green dots
appear, exit code `0` still means the suite passed.

**Note (中文)**: 现场走三条追溯链；展示 25 条需求、6 条不变量、37 个离线测试；强调每个不变量都有"被违反时会失败"的测试。

## 5. Agent governance and human supervision (7:40–9:00)

**On screen**: `AGENTS.md`, `Prompt.md`, `docs/ai-use-log.yaml`, `docs/review-memo.md`,
`transcripts/60392800-YiyangBU.md`, `.opencode/permissions.jsonc`.

**Say**:
> "The coding agent is a supervised assistant, not an unattended author. `AGENTS.md` is its single
> entry point; `Prompt.md` instructs it to produce a plan and stop for human approval before any code.
> The permission model defaults to no read and no write; every allowed path is an explicit whitelist.
> Guardrail, budget policy, and permission/rules files are frozen paths that need an ADR and human
> approval to change."

Cover the supervision evidence:
- **Plan gate**: no source code until the human approved traceability, contracts, scope boundary, and
  negative-test coverage.
- **Six CI blocking gates**: test approval, static analysis, schema, semantic evaluation, regression,
  AI-use log freshness. Show `.github/workflows/ci.yml` and the four helper scripts in `scripts/`.
- **AI-use log**: every code or prompt change appends an entry; a change touching `src/` or `prompts/`
  without a log update is blocked.
- **Annotated transcript**: six stages — requirements classification, architecture candidate
  generation and evaluation, pre-code plan approval, build, verification compliance, architecture
  revision on test evidence — with APPROVED / REDIRECTED / REJECTED / INTERRUPTED / QUESTIONED marks.
- **What the human caught that the agent did not flag**: YAML plain-scalar colon parse failure;
  integer/string schema mismatch; unmatched bracket at collection; native exceptions bypassing
  degradation; the CLI `SystemExit` contract; and a lexicon synonym gap that was fixed in the fallback
  table rather than by relaxing the whitelist.

**Note (中文)**: 讲清两类 AI 不混淆：写代码的 coding agent（被监督、被记录）与产品内嵌的可选运行时 LLM（被护栏约束）；展示人工介入标注与六类人工抓到的问题。

## 6. Debt, risks, closing (9:00–9:30)

**On screen**: `docs/debt-register.md`, `docs/architecture/risk-list.md`.

**Say**:
> "Known gaps are tracked, not hidden: a small evaluation corpus, prompt rot, frozen-code
> maintainability, hidden provider dependencies, and solo-author cognitive debt. Each has a
> mitigation and a review trigger. Future work is to expand the evaluation corpus, add a provider
> adapter test behind the live seam, and revisit retrieval-augmented categorization only if the label
> space grows. Thank you."

**Closing point**: README commands to reproduce offline tests, live tests, and the full suite; the
repository link is filled in after pushing to GitHub (account `jack2004-1`).

---

## Pre-recording checklist

- [ ] `.pennyguard/` cleared so demo data starts clean.
- [ ] No `LLM_API_KEY` or secret visible in terminal, files, or screen share.
- [ ] Offline suite green: 37 passed, 1 skipped.
- [ ] Four gate scripts run clean: schema, structural, test-approval, semantic eval.
- [ ] `eval` shows faithfulness 1.0, relevance 1.0, zero safety escapes.
- [ ] Video is a single `.mp4`, under 10 minutes, with all three required blocks.
- [ ] Speaker introduces name, student ID, group, and solo submission at the start.

## Block-to-evidence mapping (for the panel)

| Required block | Where it appears in the repo |
|---|---|
| Product demo + before/after | `src/pennyguard/app.py`, `guardrail.py`, `budget.py`, `test/offline/test_guardrail.py`, `test/offline/test_budget.py` |
| Original SE ideas | `adr/001-guarded-hybrid-classifier.md`, `evaluation-table.md`, `prompt.py`, `runtime-policy-catalog.md`, `permission-model.md` |
| Traceability | `requirements.yaml`, `trace-matrix.md`, `invariants.md`, module header ID citations, offline tests |
| Agent governance | `AGENTS.md`, `Prompt.md`, `ai-use-log.yaml`, `review-memo.md`, `transcripts/60392800-YiyangBU.md`, `ci.yml`, `scripts/` |
