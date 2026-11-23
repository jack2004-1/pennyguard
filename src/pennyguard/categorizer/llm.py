"""Optional LLM categorizer behind the Categorizer interface.

ADR: ADR-001
Implements: FR-002, PERF-002, SEC-002, INV-005

The model produces an advisory candidate only. Transport/timeout/parse failures raise
CategorizerError so the app can degrade to the rule-based fallback. The HTTP client is
injectable so offline tests never touch the network.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Optional, Protocol

from ..config import Config
from ..models import CandidateCategory, SOURCE_LLM, Transaction
from ..prompt import PromptAssembler
from .base import Categorizer, CategorizerError


class LlmClient(Protocol):
    """Minimal chat-completions client contract (provider-isolated seam)."""

    def complete(self, messages: list[dict[str, str]]) -> str: ...


class UrllibLlmClient:
    """Standard-library OpenAI-compatible chat-completions client."""

    def __init__(self, endpoint: str, api_key: str, model: str, timeout_s: float) -> None:
        self._endpoint = endpoint
        self._api_key = api_key
        self._model = model
        self._timeout_s = timeout_s

    def complete(self, messages: list[dict[str, str]]) -> str:
        body = json.dumps({"model": self._model, "messages": messages}).encode("utf-8")
        request = urllib.request.Request(
            self._endpoint,
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout_s) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError) as exc:
            # Never include the key in the raised message (SEC-001).
            raise CategorizerError(f"LLM request failed: {type(exc).__name__}") from exc

        try:
            return payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise CategorizerError("LLM response shape invalid") from exc


def _parse_model_content(raw: str) -> tuple[str, Optional[str]]:
    """Extract category/label from model text, tolerating markdown fences.

    Raises CategorizerError on malformed payload (INV-004).
    """
    text = raw.strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = text.split("\n", 1)[-1] if "\n" in text else text
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise CategorizerError("Model response is not valid JSON") from exc
    if not isinstance(data, dict):
        raise CategorizerError("Model response is not an object")
    category = data.get("category")
    if not isinstance(category, str) or not category.strip():
        raise CategorizerError("Model response missing category")
    label = data.get("label")
    return category.strip(), label if isinstance(label, str) else None


class LlmCategorizer(Categorizer):
    """LLM-backed categorizer; degrades via CategorizerError on any failure."""

    def __init__(
        self,
        config: Config,
        client: Optional[LlmClient] = None,
        assembler: Optional[PromptAssembler] = None,
    ) -> None:
        self.config = config
        self._assembler = assembler or PromptAssembler(config)
        self._client: Optional[LlmClient] = client
        if self._client is None and config.has_llm:
            self._client = UrllibLlmClient(
                endpoint=config.endpoint or "",
                api_key=config.api_key or "",
                model=config.model,
                timeout_s=config.timeout_s,
            )

    def categorize(self, transaction: Transaction) -> CandidateCategory:
        if not self.config.has_llm or self._client is None:
            raise CategorizerError("LLM not configured; use fallback categorizer")

        assembled = self._assembler.assemble(transaction)
        try:
            raw = self._client.complete(assembled.messages)
        except CategorizerError:
            raise
        except Exception as exc:  # timeout, transport, or adapter failure -> degrade
            raise CategorizerError(f"LLM call failed: {type(exc).__name__}") from exc
        category, label = _parse_model_content(raw)
        # The model is never asked for an amount; model_amount stays None (INV-002).
        return CandidateCategory(
            category=category,
            source=SOURCE_LLM,
            raw_label=label or category,
            model_amount=None,
        )
