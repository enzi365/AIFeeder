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


def _cmd_refresh(
    per_source: int,
    source_id: int | None,
    dry_run: bool,
    verbose: bool,
) -> None:
    """Fetch sources, summarize new pending items, persist. Idempotent."""
    from .refresh import run_refresh

    if not dry_run and not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY not set. Copy .env.example to .env and fill it in.")
    apply_schema()
    run_refresh(
        per_source=per_source,
        source_id=source_id,
        dry_run=dry_run,
        verbose=verbose,
    )


def _cmd_serve(host: str, port: int, reload: bool) -> None:
    """Run the local FastAPI web UI."""
    import uvicorn

    apply_schema()
    uvicorn.run(
        "aifeeder.web.app:app",
        host=host,
        port=port,
        reload=reload,
    )


def _cmd_seed_fake() -> None:
    """Populate the DB with ~12 fake items + summaries for UI dev."""
    from .seed_fake import seed_fake_items

    apply_schema()
    n = seed_fake_items()
    print(f"Seeded {n} fake items (idempotent — re-runs are no-ops).")


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
    refresh = sub.add_parser("refresh", help="Fetch sources, summarize, persist to DB")
    refresh.add_argument(
        "--per-source", type=int, default=10,
        help="Max pending items to summarize per source (default 10)",
    )
    refresh.add_argument(
        "--source-id", type=int, default=None,
        help="Limit to a single source by id (default: all)",
    )
    refresh.add_argument(
        "--dry-run", action="store_true",
        help="Fetch + parse + show what would be ingested. No AI, no DB writes.",
    )
    refresh.add_argument(
        "--quiet", action="store_true",
        help="Print final summary only. Default is verbose per-item output.",
    )
    serve = sub.add_parser("serve", help="Run the local web UI")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    serve.add_argument("--no-reload", action="store_true", help="Disable auto-reload")
    sub.add_parser(
        "seed-fake",
        help="Insert fake items + summaries for UI dev (idempotent; no API calls)",
    )

    args = parser.parse_args()
    if args.cmd == "init":
        apply_schema()
        print(f"Database initialized at {DB_PATH}")
    elif args.cmd == "preview":
        _cmd_preview(per_source=args.per_source)
    elif args.cmd == "refresh":
        _cmd_refresh(
            per_source=args.per_source,
            source_id=args.source_id,
            dry_run=args.dry_run,
            verbose=not args.quiet,
        )
    elif args.cmd == "serve":
        _cmd_serve(host=args.host, port=args.port, reload=not args.no_reload)
    elif args.cmd == "seed-fake":
        _cmd_seed_fake()
