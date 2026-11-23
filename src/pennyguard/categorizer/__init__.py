"""Categorizer package: interface, rule-based fallback, optional LLM implementation."""

from .base import Categorizer, CategorizerError
from .rule_based import RuleBasedCategorizer
from .llm import LlmCategorizer

__all__ = ["Categorizer", "CategorizerError", "RuleBasedCategorizer", "LlmCategorizer"]
