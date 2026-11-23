# PennyGuard

**AI-assisted personal-expense categorization with deterministic budget guardrails.**

- Course: CS5351 Agentic Software Engineering, 2026/27 Sem A
- Author: Yiyang BU (卜毅扬), Student ID **60392800**, Group 43 (solo)
- GitHub repository: https://github.com/jack2004-1/pennyguard

## Purpose and architecture

PennyGuard is a local command-line tool that records personal expenses and uses an AI
component to suggest a budget category from a free-text transaction description. The course
requires a genuine AI component **and** a safety-relevant boundary where AI output is constrained
by deterministic code; PennyGuard implements both.

The system splits into an **advisory layer** and an **authority layer**:

- **Advisory layer** (`categorizer/`): an optional OpenAI-compatible LLM categorizer produces a
  *candidate* category, alongside a deterministic rule-based fallback. The model has no handle
  on budgets, persistence, deletion, or any privileged action.
- **Authority layer**: a deterministic `guardrail` validates every candidate against a closed
  category whitelist, conserves the transaction amount, and structurally validates the response;
  a deterministic `BudgetPolicy` owns every over/under-budget decision; a `ledger` persists
  records locally as JSON.

The default path runs fully offline and deterministically: no network and no API key are
required. The LLM path is optional, isolated under `test/live/`, and degrades to the rule-based
fallback on any failure (no key, timeout, transport error, or malformed payload). Prompts are
versioned, assembled under a token budget with critical constraints re-injected after compaction.

See `architecture-blueprint.md` for the master constraint document and
`docs/architecture/adr/001-guarded-hybrid-classifier.md` for the architecture decision record.

## Project file organization

```
pennyguard/
├── README.md                  # this file
├── AGENTS.md                  # coding-agent entry point (D3)
├── architecture-blueprint.md  # master architecture constraint document (D2.1)
├── Prompt.md                  # static startup prompt / plan gate (D9)
├── Report.md                  # process report + reflection (D6)
├── requirements.txt          # declared dependencies
├── docs/
│   ├── req/                   # requirements.yaml, req-schema.json (D1)
│   ├── architecture/         # ADRs, invariants, trace matrix, memory, permissions, policy, eval (D2)
│   ├── code-governance/       # structural/verification constraints, tool manifest (D3/D4)
│   ├── ai-use-log.yaml        # AI usage log (GOV-002 gate object)
│   ├── review-memo.md         # per-change review verdicts (D4)
│   ├── debt-register.md       # AI-era technical debt (D4)
│   ├── bug-diary.md           # significant bugs and gaps (D4)
│   └── demo-video-script.md    # 10-minute demo video storyboard and narration
├── .opencode/                 # machine-readable permissions + always-on rules (D3)
├── .agent/rules.md            # project covenant (D3)
├── .github/workflows/ci.yml   # six blocking gates (D7)
├── prompts/                   # versioned runtime prompts
├── scripts/                   # five CI gate helper scripts
├── src/pennyguard/            # application source (D8)
├── test/
│   ├── offline/               # deterministic, network-free tests (D8)
│   └── live/                  # API-dependent tests, skipped without a key
└── transcripts/               # annotated agent session transcript (D5)
```

## How to run

### Setup (Windows / PowerShell)
```powershell
# Create and use a local virtual environment (use the interpreter full name; do not Activate.ps1)
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Use the CLI
The default path runs offline through the deterministic rule-based fallback:
```powershell
$env:PYTHONPATH = "src"
.venv\Scripts\python.exe -m pennyguard.app add --description "Coffee and toast" --amount 12.50 --date 2026-11-23
.venv\Scripts\python.exe -m pennyguard.app list
.venv\Scripts\python.exe -m pennyguard.app status
.venv\Scripts\python.exe -m pennyguard.app eval
```

### Offline deterministic tests
No network or API key required:
```powershell
.venv\Scripts\python.exe -m pytest test/offline/ -v
```

### Live API-dependent tests
Skipped automatically when `LLM_API_KEY` is not set. To run against an OpenAI-compatible
endpoint (e.g. DeepSeek):
```powershell
$env:LLM_API_KEY = "<your-key>"
$env:LLM_ENDPOINT = "<openai-compatible-chat-completions-url>"
.venv\Scripts\python.exe -m pytest test/live/ -v
```

### Full suite
```powershell
.venv\Scripts\python.exe -m pytest test/ -v
```

### Requirements schema gate
```powershell
.venv\Scripts\python.exe scripts\validate_requirements.py
```

## Blocking gates (CI)
The GitHub Actions pipeline implements six blocking gates: test approval, static analysis,
registry schema validation, semantic evaluation replay, full regression, and AI-use log freshness.
Branch protection on `main` requires the `blocking-gates` CI check to pass and disallows force
pushes and branch deletion; changes to safety-critical paths require human review with an
accompanying architecture decision. Details: `docs/code-governance/verification-constraints.md`.

## Security notes
- The API key is read only from the environment; it is never committed, logged, persisted, or
  sent in prompts. No secret is bundled in this deliverable.
- Model output is parsed into a constrained candidate object only; it never reaches a mutating,
  evaluator, or shell path.
