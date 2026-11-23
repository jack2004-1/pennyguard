"""Offline tests for the fixed evaluation replay.

Verifies: FR-006, QA-001.
"""

from pennyguard.categorizer import RuleBasedCategorizer
from pennyguard.config import Config
from pennyguard.eval import Evaluator
from pennyguard.guardrail import Guardrail


def _evaluator() -> Evaluator:
    return Evaluator(RuleBasedCategorizer(), Guardrail(Config.from_env(env={})))


def test_eval_report_zero_safety_escape():
    # verifies: FR-006 — zero safety escapes; every accepted candidate is relevant.
    report = _evaluator().run()
    assert report.safety_escapes == 0
    assert report.relevant == report.total
    assert report.total > 0
    payload = report.as_dict()
    assert "faithfulness_rate" in payload and "relevance_rate" in payload


def test_replay_deterministic():
    # verifies: QA-001 — consecutive replays are identical.
    first = _evaluator().run().as_dict()
    second = _evaluator().run().as_dict()
    assert first == second
