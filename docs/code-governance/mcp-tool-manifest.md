# MCP Tool Manifest (D3)

Tools an AI coding agent may call, and which roles may call them. Default for any tool not
listed: unavailable. Guard rules are enforced in `.opencode/permissions.jsonc`.

| Tool ID | Description | Plan agent | Coding agent | Verification agent | Guard rules |
|---|---|---|---|---|---|
| `fs.read` | Read an allowed file under the read whitelist. | yes | yes | yes | Denied for secret-bearing env; only whitelisted globs. |
| `fs.write` | Create/modify a file in the write whitelist. | no | yes | no | Frozen paths blocked; only the plan-named module + paired test; append-only to log/memo files. |
| `test.run-offline` | Run the deterministic offline pytest suite. | no | yes | yes | Must not require network or key; full suite for regression gate. |
| `test.run-live` | Run API-dependent live tests. | no | yes | yes | Auto-skipped without `LLM_API_KEY`; never blocks offline CI. |
| `req.validate` | Validate requirements registry against schema (`scripts/validate_requirements.py`). | yes | yes | yes | Schema gate; blocks on invalid registry. |
| `eval.replay` | Replay the fixed evaluation set and report metrics. | no | yes | yes | Semantic gate; thresholds recorded in `eval.py`. |
| `log.append` | Append an entry to `docs/ai-use-log.yaml`. | no | yes | yes | Required whenever code/prompt changes (GOV-002). |
| `doc.append-memo` | Append a review memo / bug diary / debt register entry. | no | no | yes | Human/verification authorship; coding agent does not self-approve. |
| `shell.exec` | Run a restricted command (test runner, validator). | no | yes | yes | Frozen paths and secret access blocked; no destructive or network-mutating command. |
| `repo.search` | Search within repository text. | yes | yes | yes | Read-only; no outbound web or credential lookup. |

## Tool-use rules
- The coding agent cannot call a tool outside its role row; a denied call is recorded as an
  attempt and reviewed.
- No tool reads or echoes the API key; secret redaction applies to every surfaced string.
- Tool outputs that touch safety-critical paths are routed through the verification agent and
  human review before merge.
- New tools must be added here and in the machine-readable permission model before use.
