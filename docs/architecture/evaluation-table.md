# Candidate Architecture Evaluation Table (D2.8)

Scores: 5 = strongest, 1 = weakest. Criteria follow the architectural drivers in the
blueprint. Weight reflects course priorities: an enforceable safety boundary and offline
determinism are weighted highest.

## 1. Weighted criteria

| Criterion | Weight | Definition |
|---|---|---|
| Enforceable safety boundary | 0.25 | Can deterministic code block unsafe model output without relying on model compliance. |
| Offline determinism | 0.20 | Default path runs without network/secret; repeated replays are identical. |
| Genuine AI component | 0.15 | Contains a real LLM/AI-assisted decision path, not a rules-only wrapper. |
| Cost & latency control | 0.15 | Bounded prompt size, call timeout, optional model use. |
| Maintainability | 0.12 | Small surface, clear contracts, one module per element. |
| Traceability | 0.13 | Requirement → component → test → monitor mapping is straightforward. |

## 2. Candidate scoring

| Candidate | Safety boundary | Offline determinism | AI component | Cost/latency | Maintainability | Traceability | Weighted total |
|---|---|---|---|---|---|---|---|
| **A. Guarded hybrid (chosen)** | 5 | 5 | 4 | 4 | 4 | 5 | **4.55** |
| B. Model-direct write to ledger | 1 | 2 | 4 | 2 | 3 | 2 | 2.30 |
| C. Rules-only, no model | 5 | 5 | 1 | 5 | 5 | 4 | 4.10 |
| D. Retrieval-augmented over local corpus | 3 | 3 | 4 | 3 | 2 | 3 | 3.05 |
| E. Separate model microservice over HTTP | 3 | 2 | 4 | 2 | 2 | 3 | 2.80 |

Weighted total = Σ(score × weight). Weights: 0.25 / 0.20 / 0.15 / 0.15 / 0.12 / 0.13.

## 3. Rationale

- **A (guarded hybrid)** wins because it places an authoritative deterministic guardrail and
  budget policy between the model and the ledger, satisfies the genuine-AI requirement, and
  keeps the offline path primary. Its only soft spot is two classifier implementations,
  addressed by a shared interface and paired tests.
- **B** fails the central safety requirement: unsafe output cannot be reliably blocked.
- **C** is deterministic and maintainable but lacks the required AI component.
- **D** adds index/storage complexity and non-determinism that a small closed label set does
  not justify; it remains a reopen option (see option ledger).
- **E** over-engineers a solo local CLI and introduces a service dependency in the baseline.

## 4. Evidence basis
- Course spec §1: at least one genuine AI component and at least one safety-relevant boundary.
- Requirements INV-001…006, SEC-001/002, QA-001, COST-001, PERF-002.
- Offline fixture behavior measured in `test/offline/`; eval thresholds in `eval.py`.
