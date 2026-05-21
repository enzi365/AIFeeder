"""CLI entry point. For v1 slice: stdout summary preview before persisting."""
import argparse
import os

from dotenv import load_dotenv

from .db import DB_PATH, apply_schema


def _cmd_preview(per_source: int = 3) -> None:
    """Fetch each source, summarize the first N items, print to stdout. No DB writes."""
    # Imports here so `init` works without OPENAI_API_KEY.
    from .ai import summarize
    from .ingest import fetch_feed, fetch_sources

    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY not set. Copy .env.example to .env and fill it in.")

    apply_schema()  # idempotent; covers "ran preview before init"
    sources = fetch_sources()
    if not sources:
        raise SystemExit("No sources found. Run `aifeeder init` first.")

    total_cost = 0.0
    for src in sources:
        print(f"\n=== {src['name']} ===")
        print(f"URL: {src['url']}")
        print(f"Why: {src['why']}\n")
        try:
            raw_items = fetch_feed(src["url"])[:per_source]
        except Exception as e:
            print(f"  [feed fetch failed: {e}]")
            continue
        if not raw_items:
            print("  [no items in feed]")
            continue
        for item in raw_items:
            print(f"--- {item.title or '[no title]'} ---")
            print(f"    {item.url}")
            try:
                s = summarize(content=item.raw_content, why=src["why"], title=item.title)
            except Exception as e:
                print(f"    ERROR: {type(e).__name__}: {e}\n")
                continue
            print(f"    Verdict:    {s.relevance_verdict}  (confidence {s.confidence:.2f})")
            print(f"    Reason:     {s.relevance_reason}")
            print(f"    Type:       {s.content_type_tag}  ·  Style: {s.style_tag}  ·  Read time: {s.read_time_estimate}")
            print(f"    Purpose:    {s.purpose}")
            print(f"    Cost:       ${s.cost_usd:.4f}  (tokens in/out: {s.tokens_in}/{s.tokens_out})")
            print(f"    Key points:")
            for bullet in s.key_points:
                print(f"      • {bullet}")
            print()
            total_cost += s.cost_usd
    print(f"\n=== Preview total cost: ${total_cost:.4f} ===")


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(prog="aifeeder")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init", help="Initialize the database (apply schema + seed sources)")
    preview = sub.add_parser(
        "preview",
        help="Fetch sources, summarize a few items, print to stdout (no DB writes)",
    )
    preview.add_argument(
        "--per-source", type=int, default=3,
        help="Items to summarize per source (default 3)",
    )
    sub.add_parser("refresh", help="Fetch sources, summarize, persist to DB")

    args = parser.parse_args()
    if args.cmd == "init":
        apply_schema()
        print(f"Database initialized at {DB_PATH}")
    elif args.cmd == "preview":
        _cmd_preview(per_source=args.per_source)
    elif args.cmd == "refresh":
        raise NotImplementedError("Implementing after preview validates the prompt")
