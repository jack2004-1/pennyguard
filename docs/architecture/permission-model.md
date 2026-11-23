# Permission Model (D2.6)

File-level read/write rights per AI agent role. **Default: no read, no write.** Every
allowed path is an explicit whitelist below. Machine-readable mirror:
`.opencode/permissions.jsonc`.

## 1. Roles
- **Plan agent**: produces the execution plan and traceability/contract analysis; writes no source.
- **Coding agent**: implements the assigned module and its tests under an approved plan.
- **Verification agent**: runs tests and checks fitness/structural rules; writes no source fix.
- **Human owner**: sole approver for plans, critical-path changes, and merges.
- **Runtime application** (not an agent): its filesystem access is limited to the local data dir.

## 2. Path whitelist

| Path / glob | Plan agent | Coding agent | Verification agent | Notes |
|---|---|---|---|---|
| `docs/req/**` | read | read | read | Requirements registry and schema. |
| `docs/architecture/**` | read | read | read | Blueprint, ADRs, invariants, matrices. |
| `docs/code-governance/**` | read | read | read | Structural/verification constraints, tool manifest. |
| `AGENTS.md`, `architecture-blueprint.md`, `Prompt.md` | read | read | read | Entry-point and master constraint docs. |
| `src/pennyguard/<assigned-module>.py` | none | read, write | read | Only the module named in the approved plan. |
| `test/offline/test_<module>.py` | none | read, write | read | Test paired with the assigned module. |
| `test/live/**` | none | read | read | Live tests; skipped without key. |
| `prompts/prompt_v*.yaml` | read | read, write (versioned) | read | New version file; old versions stay frozen. |
| `docs/ai-use-log.yaml` | none | append | read | Updated whenever code/prompt changes (GOV-002). |
| `src/pennyguard/guardrail.py` | read | **frozen** | read | Safety-critical: change needs ADR + human approval (GOV-003). |
| `src/pennyguard/budget.py` | read | **frozen** | read | Safety-critical: compliance authority. |
| `.opencode/**`, `.agent/**` | read | **frozen** | read | Permission/rules files; human-maintained. |
| `docs/review-memo.md`, `docs/bug-diary.md`, `docs/debt-register.md` | none | append | read | QA records written after review. |
| Environment secret (`LLM_API_KEY`) | **no read** | **no read** | **no read** | Never exposed to the agent; runtime reads it directly. |
| Any path not listed | denied | denied | denied | Default deny. |

## 3. Enforcement
- The coding agent cannot create or modify files outside its whitelist; violations are
  blocked by `.opencode/permissions.jsonc` guard rules and flagged in review.
- Frozen safety-critical paths appear in branch protection: a touching PR requires CI pass,
  an ADR reference, and an approving human review.
- The agent never receives the API key; redaction is applied to any surfaced environment.
- Permission changes themselves are human-only and recorded as an ADR/review memo.
