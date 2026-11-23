# Option Ledger (D2.11)

Rejected architectural options, with the conditions under which they should be reconsidered.

| Rejected option | Why rejected now | Reopen trigger |
|---|---|---|
| Model-direct output written to the ledger | No enforceable whitelist/amount/compliance control; violates INV-001/002/003 and SEC-002. | Do not reopen unless the boundary model changes; guardrail layer remains mandatory regardless. |
| Rules-only implementation | Fails the course requirement for a genuine AI component. | Not applicable as a baseline; rules-only stays as the fallback path only. |
| Retrieval-augmented categorization over a local corpus | Index/storage overhead and non-determinism for a small closed label set. | Reopen if the label space grows, keyword recall falls below the relevance threshold on a realistic fixture, or descriptions become domain-specific. |
| Separate model microservice over HTTP | Service dependency and deployment complexity for a solo local CLI. | Reopen if multiple clients share one model policy or the runtime must run on a separate host. |
| Multi-label tagging | Complicates the whitelist guardrail and single-label policy. | Reopen if users need categories such as "food + transport" on one record; guardrail would need a list-of-labels check. |
| Database-backed ledger (SQLite/Postgres) | Single JSON file is sufficient and fully inspectable for this baseline. | Reopen if concurrency, querying, or multi-account features enter scope. |
| Bundled third-party LLM SDK | Avoid SDK lock-in and reduce dependency/security surface; standard-library HTTP suffices. | Reopen only if a required provider cannot be reached over the OpenAI-compatible HTTP interface. |
