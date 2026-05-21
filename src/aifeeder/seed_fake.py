"""Fake data fixtures for UI dev. Idempotent — re-runs are no-ops.

12 items across the 9 content_type_tags, mixed read-time buckets. Tied to the
two seeded sources (Simon Willison, ArXiv: AI). Run via `aifeeder seed-fake`.
"""
import json
from contextlib import closing

from .db import connect

_FAKE_ITEMS: list[dict] = [
    {
        "source_name": "Simon Willison",
        "external_id": "fake-1",
        "url": "https://example.com/fake/llm-tool-use-tutorial",
        "title": "Practical tool-use with smaller LLMs: a hands-on tutorial",
        "raw_content": "A walkthrough of building reliable tool-use loops with smaller models. Covers schema design for function calling, retry on malformed JSON, and how to detect when the model is hallucinating tool arguments versus calling them correctly. Includes a working Python example using OpenAI's function-calling API against gpt-4o-mini and gpt-4.1-mini, with side-by-side benchmarks. The key insight: schema strictness matters more than model size for reliability.",
        "relevance_verdict": "yes",
        "confidence": 0.92,
        "relevance_reason": "Worth reading if you're building agents on smaller models and want a working reliability pattern.",
        "content_type_tag": "tutorial",
        "style_tag": "technical-deep-dive",
        "purpose": "Show that smaller LLMs can be reliable for tool-use if you design the schema right.",
        "read_time_estimate": "medium",
        "key_points": [
            "Schema strictness matters more than model size for tool-use reliability",
            "Retry-on-malformed-JSON is necessary even with function calling",
            "Side-by-side benchmark: gpt-4o-mini matches gpt-4.1 for narrow tool-use tasks",
            "Hallucinated arguments are detectable via schema validation, not via the model",
        ],
    },
    {
        "source_name": "Simon Willison",
        "external_id": "fake-2",
        "url": "https://example.com/fake/llm-essay-context-window",
        "title": "The context window is not your friend",
        "raw_content": "An opinionated essay arguing that the 'just stuff more context in' approach is masking real engineering problems. Long contexts hide retrieval failures, push costs up sublinearly with quality gains, and lead to lazy prompt design. The author makes the case for retrieval-augmented patterns over context-stuffing for any production system serving more than a handful of users.",
        "relevance_verdict": "yes",
        "confidence": 0.85,
        "relevance_reason": "Worth reading if you've been tempted to solve a retrieval problem by paying for a bigger context window.",
        "content_type_tag": "essay",
        "style_tag": "opinionated",
        "purpose": "Argue that long-context as a substitute for retrieval is engineering laziness.",
        "read_time_estimate": "quick",
        "key_points": [
            "Long contexts hide retrieval failures rather than fixing them",
            "Cost scales sublinearly but quality gains plateau fast",
            "RAG-first design pressures you to actually understand your data",
            "Context-stuffing is a smell in any system with >10 users",
        ],
    },
    {
        "source_name": "ArXiv: AI",
        "external_id": "fake-3",
        "url": "https://arxiv.org/abs/2511.fake3",
        "title": "Self-correcting agents via structured reflection chains",
        "raw_content": "We introduce STRUCT-REFLECT, a method for improving multi-step agent task completion through structured intermediate reflection between tool calls. Unlike free-form chain-of-thought, STRUCT-REFLECT requires the agent to commit to a typed self-evaluation after each tool call: classifying the outcome as 'progressed', 'stalled', or 'regressed', plus a one-sentence why. We show 14-22% improvements on SWE-bench and WebArena over baseline ReAct, with no fine-tuning. Ablations show the typed labels do most of the work — the free-form why-line is supporting evidence at best.",
        "relevance_verdict": "yes",
        "confidence": 0.78,
        "relevance_reason": "Worth a shot for the structured-reflection technique, although the gains are likely smaller in production than the benchmark suggests.",
        "content_type_tag": "research paper",
        "style_tag": "technical-deep-dive",
        "purpose": "Propose typed intermediate reflection as a cheap upgrade to ReAct-style agent loops.",
        "read_time_estimate": "long",
        "key_points": [
            "STRUCT-REFLECT: typed self-evaluation labels between agent tool calls",
            "14-22% improvement over baseline ReAct on SWE-bench and WebArena",
            "Ablation: typed labels do most of the lifting, free-form text is secondary",
            "No fine-tuning required — works as a pure prompting technique",
            "Hyperparameter-light: only the label vocabulary needs design",
        ],
    },
    {
        "source_name": "ArXiv: AI",
        "external_id": "fake-4",
        "url": "https://arxiv.org/abs/2511.fake4",
        "title": "Provable bounds for attention-head pruning in dense transformers",
        "raw_content": "We derive analytic upper bounds on the L2 distortion induced by removing individual attention heads from a trained dense transformer, under mild assumptions on the data distribution. We prove that heads with low effective rank in their value-projection matrices are removable with bounded quality loss, and characterise the regime in which the bound is tight.",
        "relevance_verdict": "no",
        "confidence": 0.88,
        "relevance_reason": "Skip — this is mostly formal proof work without an applied recipe you'd use day-to-day.",
        "content_type_tag": "research paper",
        "style_tag": "technical-deep-dive",
        "purpose": "Provide theoretical justification for attention-head pruning heuristics.",
        "read_time_estimate": "long",
        "key_points": [
            "Analytic upper bound on L2 distortion from head removal",
            "Low value-projection effective rank predicts removability",
            "Proof-heavy, no implementation",
        ],
    },
    {
        "source_name": "Simon Willison",
        "external_id": "fake-5",
        "url": "https://example.com/fake/openai-pricing-news",
        "title": "OpenAI cuts gpt-4o-mini prices by 30%",
        "raw_content": "OpenAI announced a 30% price cut on gpt-4o-mini effective immediately. Input tokens drop to $0.105 per million, output to $0.42 per million. The announcement coincides with a new batch-processing tier offering an additional 50% discount for non-real-time workloads.",
        "relevance_verdict": "maybe",
        "confidence": 0.65,
        "relevance_reason": "Worth a glance if you're cost-sensitive on summarization workloads — otherwise skim the headline.",
        "content_type_tag": "news",
        "style_tag": "news-brief",
        "purpose": "Report a pricing change in the OpenAI API.",
        "read_time_estimate": "quick",
        "key_points": [
            "gpt-4o-mini input: $0.105/M tokens (down from $0.15)",
            "Output: $0.42/M tokens (down from $0.60)",
            "Batch tier offers another 50% off for non-real-time use",
        ],
    },
    {
        "source_name": "Simon Willison",
        "external_id": "fake-6",
        "url": "https://example.com/fake/link-blog-claude-skills",
        "title": "Notes on Claude Skills and the discoverability problem",
        "raw_content": "A short link-blog post collecting reactions to Anthropic's recent Skills feature, plus the author's own take. The interesting bit is the discoverability problem: skills only work if the model knows to invoke them, which depends on the description quality more than the skill quality. Links to four reactions plus the original announcement.",
        "relevance_verdict": "yes",
        "confidence": 0.80,
        "relevance_reason": "Worth reading if you're building agent platforms — the discoverability framing transfers to any tool/skill registry.",
        "content_type_tag": "link blog",
        "style_tag": "conversational",
        "purpose": "Aggregate reactions to Claude Skills and surface the discoverability framing.",
        "read_time_estimate": "quick",
        "key_points": [
            "Skill *description* quality matters more than skill quality",
            "Discoverability problem generalises to any tool/skill registry",
            "Four reaction links + the original announcement",
        ],
    },
    {
        "source_name": "Simon Willison",
        "external_id": "fake-7",
        "url": "https://example.com/fake/interview-anthropic-researcher",
        "title": "Interview: an Anthropic researcher on Claude 4 capabilities",
        "raw_content": "A 45-minute interview with a researcher on Claude 4's reasoning capabilities, training approach, and the surprises that emerged. Discusses why scaled-up RL is producing qualitatively different behaviour than supervised fine-tuning, and where the team thinks the next frontier is.",
        "relevance_verdict": "maybe",
        "confidence": 0.70,
        "relevance_reason": "Worth a shot for the RL-scaling discussion, although interview format means signal-density is lower than a written piece.",
        "content_type_tag": "interview",
        "style_tag": "conversational",
        "purpose": "Surface insider perspective on Claude 4 capabilities and where reasoning is headed.",
        "read_time_estimate": "long",
        "key_points": [
            "Scaled-up RL produces qualitatively different behaviour than SFT",
            "Reasoning improvements are training-driven, not architecture-driven",
            "Frontier framing: long-horizon tasks over short-horizon benchmarks",
        ],
    },
    {
        "source_name": "Simon Willison",
        "external_id": "fake-8",
        "url": "https://example.com/fake/review-langgraph-vs-pydantic-ai",
        "title": "Reviewing LangGraph vs Pydantic-AI for agent orchestration",
        "raw_content": "Side-by-side review of two agent orchestration frameworks. LangGraph wins on graph-shaped flows and visualisation tooling; Pydantic-AI wins on type safety and minimal API surface. Concludes that the choice should come down to your team's typing culture, not framework features.",
        "relevance_verdict": "yes",
        "confidence": 0.82,
        "relevance_reason": "Worth reading if you're picking between agent frameworks — the team-typing-culture framing is the right decision lens.",
        "content_type_tag": "review",
        "style_tag": "explainer",
        "purpose": "Compare LangGraph and Pydantic-AI on practical agent-orchestration concerns.",
        "read_time_estimate": "medium",
        "key_points": [
            "LangGraph: graph-shaped flows, visualisation tooling",
            "Pydantic-AI: type safety, minimal API surface",
            "Recommendation: choose by team typing culture, not feature list",
            "Both production-ready for typical agent use cases",
        ],
    },
    {
        "source_name": "Simon Willison",
        "external_id": "fake-9",
        "url": "https://example.com/fake/thread-prompt-injection",
        "title": "Thread: every prompt-injection defence I've tried, ranked",
        "raw_content": "A long thread enumerating the author's attempted defences against prompt injection in production systems. Ranks them by effectiveness against a held-out attack set. Spoiler: nothing fully works; the best defence is architectural (don't put untrusted text and high-privilege tools in the same context).",
        "relevance_verdict": "yes",
        "confidence": 0.90,
        "relevance_reason": "Worth reading if you're shipping anything that processes user-controlled text — the architectural framing is the whole takeaway.",
        "content_type_tag": "thread",
        "style_tag": "reflective",
        "purpose": "Share a practitioner's ranked list of attempted prompt-injection defences.",
        "read_time_estimate": "medium",
        "key_points": [
            "Nothing fully prevents prompt injection at the prompt layer",
            "Architectural separation (untrusted text away from privileged tools) is the only robust defence",
            "Output filtering and re-prompting buy modest improvements",
            "Per-defence numbers on a held-out attack set",
        ],
    },
    {
        "source_name": "ArXiv: AI",
        "external_id": "fake-10",
        "url": "https://arxiv.org/abs/2511.fake10",
        "title": "Memory-efficient fine-tuning via gradient checkpointing rediscovered",
        "raw_content": "A short note covering recent rediscoveries of gradient-checkpointing strategies in the context of small-model fine-tuning. The piece itself is mostly historical recap with one new empirical observation about activation reuse.",
        "relevance_verdict": "no",
        "confidence": 0.80,
        "relevance_reason": "Skip — this is mostly historical recap and the new contribution is narrow.",
        "content_type_tag": "other",
        "style_tag": "explainer",
        "purpose": "Recap historical gradient-checkpointing work with one minor empirical addition.",
        "read_time_estimate": "medium",
        "key_points": [
            "Historical recap of gradient-checkpointing rediscoveries",
            "One new empirical observation on activation reuse",
            "Limited practical takeaway for new fine-tuners",
        ],
    },
    {
        "source_name": "Simon Willison",
        "external_id": "fake-11",
        "url": "https://example.com/fake/tutorial-sqlite-vector",
        "title": "Tutorial: SQLite as a vector store for small RAG apps",
        "raw_content": "Walks through using SQLite's vss extension as a vector store for small-to-medium RAG applications. Covers index choice, recall/latency tradeoffs at common scales (1K, 10K, 100K vectors), and when to graduate to a dedicated vector DB. Includes runnable Python.",
        "relevance_verdict": "yes",
        "confidence": 0.88,
        "relevance_reason": "Worth reading if your RAG app is under 100K vectors and you're tired of running a separate vector service.",
        "content_type_tag": "tutorial",
        "style_tag": "explainer",
        "purpose": "Show that SQLite is a viable vector store for small RAG applications.",
        "read_time_estimate": "medium",
        "key_points": [
            "SQLite vss extension covers RAG up to ~100K vectors",
            "Recall/latency benchmarks at 1K / 10K / 100K scales",
            "Graduation criteria: when to move to a dedicated vector DB",
            "Runnable Python example included",
        ],
    },
    {
        "source_name": "Simon Willison",
        "external_id": "fake-12",
        "url": "https://example.com/fake/essay-mindful-consumption",
        "title": "On reading less but reading better",
        "raw_content": "A reflective essay on shifting from quantity-driven to quality-driven reading in a world of infinite content. The author argues that the bottleneck is no longer access but attention, and proposes a practice of articulating why-you-read before every consumption session.",
        "relevance_verdict": "yes",
        "confidence": 0.86,
        "relevance_reason": "Worth reading if you're working on mindful-consumption tooling — the why-articulation practice maps directly to per-source 'why'.",
        "content_type_tag": "essay",
        "style_tag": "reflective",
        "purpose": "Argue for an intent-first reading practice in response to content abundance.",
        "read_time_estimate": "quick",
        "key_points": [
            "Attention, not access, is the new bottleneck",
            "Articulating why-you-read before consumption changes what you notice",
            "Quality-over-quantity is a practice, not an aesthetic preference",
            "Resists the inbox-zero metaphor in favour of a library metaphor",
        ],
    },
]


def seed_fake_items() -> int:
    """Insert the fake items + summaries. Returns the count inserted (0 if all already present)."""
    inserted = 0
    with closing(connect()) as conn:
        for item in _FAKE_ITEMS:
            src_row = conn.execute(
                "SELECT id FROM sources WHERE name = ?", (item["source_name"],)
            ).fetchone()
            if src_row is None:
                continue
            source_id = src_row["id"]

            cur = conn.execute(
                """
                INSERT OR IGNORE INTO items (source_id, external_id, url, title, raw_content, status)
                VALUES (?, ?, ?, ?, ?, 'processed')
                """,
                (source_id, item["external_id"], item["url"], item["title"], item["raw_content"]),
            )
            if cur.rowcount == 0:
                continue
            item_id = cur.lastrowid
            inserted += 1

            conn.execute(
                """
                INSERT INTO summaries (
                    item_id, relevance_verdict, confidence, relevance_reason,
                    content_type_tag, style_tag, purpose, read_time_estimate,
                    key_points_json, model_used
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item_id,
                    item["relevance_verdict"],
                    item["confidence"],
                    item["relevance_reason"],
                    item["content_type_tag"],
                    item["style_tag"],
                    item["purpose"],
                    item["read_time_estimate"],
                    json.dumps(item["key_points"]),
                    "fake-seed",
                ),
            )
        conn.commit()
    return inserted
