"""Live API-dependent tests.

Skipped automatically when LLM_API_KEY is not set (D8 separation). These tests reach a real
OpenAI-compatible endpoint and are never part of the offline deterministic suite.
"""

import os
from decimal import Decimal

import pytest

from pennyguard.categorizer.llm import LlmCategorizer
from pennyguard.config import Config
from pennyguard.models import CATEGORIES, Transaction

pytestmark = pytest.mark.skipif(
    not os.environ.get("LLM_API_KEY"), reason="LLM_API_KEY not set; live tests skipped"
)


def test_live_categorize_returns_whitelist_category():
    config = Config.from_env(env=dict(os.environ))
    llm = LlmCategorizer(config)
    tx = Transaction(id="live-1", description="Coffee shop downtown", amount=Decimal("12"), date="2026-11-01")
    candidate = llm.categorize(tx)
    assert candidate.category in CATEGORIES
