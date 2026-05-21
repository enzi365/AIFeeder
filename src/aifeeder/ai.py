"""Provider-agnostic summarization. summarize() is the only public function.

Provider routing: model name prefix decides vendor.
  'gpt-*' / 'o3-*' / 'o4-*' → OpenAI
  'claude-*'                → Anthropic

Add a model to PRICES below when adding it to the rotation.
"""
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "summarize_v1.txt"

CONTENT_TYPE_TAGS = [
    "tutorial", "essay", "research paper", "news",
    "link blog", "interview", "review", "thread", "other",
]

STYLE_TAGS = [
    "technical-deep-dive", "explainer", "opinionated",
    "conversational", "reflective", "news-brief", "narrative",
]

READ_TIME_BUCKETS = ["quick", "medium", "long"]

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
    confidence: float
    relevance_reason: str
    content_type_tag: str
    style_tag: str
    purpose: str
    read_time_estimate: Literal["quick", "medium", "long"]
    key_points: list[str]
    chapter_index: list[dict] | None  # reserved; not populated in v1
    model_used: str
    tokens_in: int
    tokens_out: int
    cost_usd: float


def summarize(
    content: str,
    why: str,
    title: str = "",
    model: str | None = None,
) -> Summary:
    """Summarize content against the user's 'why' intent."""
    model = model or os.environ.get("AIFEEDER_MODEL", "gpt-4o-mini")
    if model.startswith(("gpt-", "o3-", "o4-")):
        return _summarize_openai(content, why, title, model)
    if model.startswith("claude-"):
        return _summarize_anthropic(content, why, title, model)
    raise ValueError(f"Unknown model provider for: {model}")


_SUMMARIZE_TOOL = {
    "type": "function",
    "function": {
        "name": "summarize",
        "description": "Produce a structured summary and relevance verdict.",
        "parameters": {
            "type": "object",
            "properties": {
                "relevance_verdict": {
                    "type": "string",
                    "enum": ["yes", "no", "maybe"],
                },
                "confidence": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                },
                "relevance_reason": {"type": "string"},
                "content_type_tag": {
                    "type": "string",
                    "enum": CONTENT_TYPE_TAGS,
                    "description": "Format of the piece.",
                },
                "style_tag": {
                    "type": "string",
                    "enum": STYLE_TAGS,
                    "description": "Dominant style of the piece.",
                },
                "purpose": {
                    "type": "string",
                    "description": "What the author is trying to do, one sentence in author-voice.",
                },
                "read_time_estimate": {
                    "type": "string",
                    "enum": READ_TIME_BUCKETS,
                    "description": "quick (<5min), medium (5-15min), long (>15min).",
                },
                "key_points": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 3,
                    "maxItems": 6,
                },
            },
            "required": [
                "relevance_verdict", "confidence", "relevance_reason",
                "content_type_tag", "style_tag", "purpose",
                "read_time_estimate", "key_points",
            ],
            "additionalProperties": False,
        },
    },
}


def _summarize_openai(content: str, why: str, title: str, model: str) -> Summary:
    from openai import OpenAI

    client = OpenAI()
    system_prompt = PROMPT_PATH.read_text()
    user_msg = (
        f'Source "why": {why}\n\n'
        f'Title: {title or "[no title]"}\n\n'
        f"Content: {content}"
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg},
        ],
        tools=[_SUMMARIZE_TOOL],
        tool_choice={"type": "function", "function": {"name": "summarize"}},
    )

    msg = response.choices[0].message
    if not msg.tool_calls:
        raise RuntimeError(f"Model returned no tool call: {msg.content!r}")
    args = json.loads(msg.tool_calls[0].function.arguments)

    usage = response.usage
    tokens_in = usage.prompt_tokens
    tokens_out = usage.completion_tokens

    return Summary(
        relevance_verdict=args["relevance_verdict"],
        confidence=args["confidence"],
        relevance_reason=args["relevance_reason"],
        content_type_tag=args["content_type_tag"],
        style_tag=args["style_tag"],
        purpose=args["purpose"],
        read_time_estimate=args["read_time_estimate"],
        key_points=args["key_points"],
        chapter_index=None,
        model_used=model,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        cost_usd=cost_usd(model, tokens_in, tokens_out),
    )


def _summarize_anthropic(content: str, why: str, title: str, model: str) -> Summary:
    raise NotImplementedError("Provider abstraction stub — OpenAI is default in v1")


def cost_usd(model: str, tokens_in: int, tokens_out: int) -> float:
    if model not in PRICES:
        raise ValueError(f"No price entry for model: {model}. Add to PRICES dict.")
    in_price, out_price = PRICES[model]
    return (tokens_in / 1_000_000) * in_price + (tokens_out / 1_000_000) * out_price
