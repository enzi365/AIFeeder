"""Provider-agnostic summarization. summarize() is the only public function.

Provider routing: model name prefix decides vendor.
  'gpt-*' / 'o3-*' / 'o4-*' → OpenAI
  'claude-*'                → Anthropic

Add a model to PRICES below when adding it to the rotation.
"""
import os
from dataclasses import dataclass
from typing import Literal

# Cost per 1M tokens (input, output) in USD. Update manually when prices change.
PRICES: dict[str, tuple[float, float]] = {
    # OpenAI
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4.1-mini": (0.40, 1.60),
    "gpt-4.1": (2.00, 8.00),
    "gpt-4o": (2.50, 10.00),
    # Anthropic (approximate — verify on anthropic.com/pricing before relying on)
    "claude-haiku-4-5-20251001": (1.00, 5.00),
    "claude-sonnet-4-6": (3.00, 15.00),
}


@dataclass
class Summary:
    relevance_verdict: Literal["yes", "no", "maybe"]
    relevance_reason: str
    content_type_tag: str
    key_points: list[str]
    chapter_index: list[dict] | None  # reserved; not populated in v1
    model_used: str
    tokens_in: int
    tokens_out: int
    cost_usd: float


def summarize(content: str, why: str, model: str | None = None) -> Summary:
    """Summarize content against the user's 'why' intent."""
    model = model or os.environ.get("AIFEEDER_MODEL", "gpt-4o-mini")
    if model.startswith(("gpt-", "o3-", "o4-")):
        return _summarize_openai(content, why, model)
    if model.startswith("claude-"):
        return _summarize_anthropic(content, why, model)
    raise ValueError(f"Unknown model provider for: {model}")


def _summarize_openai(content: str, why: str, model: str) -> Summary:
    raise NotImplementedError("Prompt design pending user A-checkpoint")


def _summarize_anthropic(content: str, why: str, model: str) -> Summary:
    raise NotImplementedError("Provider abstraction stub — OpenAI is default in v1")


def cost_usd(model: str, tokens_in: int, tokens_out: int) -> float:
    if model not in PRICES:
        raise ValueError(f"No price entry for model: {model}. Add to PRICES dict.")
    in_price, out_price = PRICES[model]
    return (tokens_in / 1_000_000) * in_price + (tokens_out / 1_000_000) * out_price
