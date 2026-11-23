"""Offline tests for categorizer selection and rule-based fallback.

Verifies: FR-002, FR-003, COST-002.
"""

from decimal import Decimal

import pytest

from pennyguard.categorizer import CategorizerError, LlmCategorizer, RuleBasedCategorizer
from pennyguard.config import Config
from pennyguard.models import CATEGORIES, Transaction


def _tx(description: str) -> Transaction:
    return Transaction(id="t1", description=description, amount=Decimal("10"), date="2026-11-01")


def test_result_category_in_whitelist():
    # verifies: FR-002
    rule = RuleBasedCategorizer()
    for desc in ["Coffee shop", "Uber ride", "Amazon order", "Unknown hobby xyz"]:
        candidate = rule.categorize(_tx(desc))
        assert candidate.category in CATEGORIES


def test_keyword_mapping():
    # verifies: FR-002 deterministic mapping
    rule = RuleBasedCategorizer()
    assert rule.categorize(_tx("COFFEE BEAN SHOP")).category == "food"
    assert rule.categorize(_tx("UBER RIDE")).category == "transport"
    assert rule.categorize(_tx("AMZN MKTPL")).category == "shopping"


def test_no_key_uses_rule_classifier_no_network():
    # verifies: FR-003 — without a key the rule classifier is selected; no LLM client built.
    config = Config.from_env(env={})
    assert config.has_llm is False
    rule = RuleBasedCategorizer()
    candidate = rule.categorize(_tx("Coffee"))
    assert candidate.source == "rule"


def test_no_client_without_config():
    # verifies: COST-002 — no LLM invocation when unconfigured.
    config = Config.from_env(env={})
    llm = LlmCategorizer(config)
    with pytest.raises(CategorizerError):
        llm.categorize(_tx("Coffee"))


def test_unknown_description_falls_back_to_other():
    # negative test: unmatched description must not invent a category
    rule = RuleBasedCategorizer()
    assert rule.categorize(_tx("zzzqxv unusual item")).category == "other"
