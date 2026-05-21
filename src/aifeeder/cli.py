"""CLI entry point. For v1 slice: stdout summary preview before persisting."""
import argparse

from .db import DB_PATH, apply_schema


def main() -> None:
    parser = argparse.ArgumentParser(prog="aifeeder")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init", help="Initialize the database (apply schema + seed sources)")
    sub.add_parser(
        "preview",
        help="Fetch sources, summarize a few items, print to stdout (no DB writes)",
    )
    sub.add_parser("refresh", help="Fetch sources, summarize, persist to DB")

    args = parser.parse_args()
    if args.cmd == "init":
        apply_schema()
        print(f"Database initialized at {DB_PATH}")
    elif args.cmd == "preview":
        raise NotImplementedError("AI prompt pending user A-checkpoint")
    elif args.cmd == "refresh":
        raise NotImplementedError("Implementing after AI prompt + ingestion land")
