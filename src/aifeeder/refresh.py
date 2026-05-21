"""Refresh: fetch new items from sources, summarize, persist.

Bridges RSS → filtered, intent-aware feed entries. Per-item commit: each
item's summary is its own transaction so a crash mid-run leaves clean
partial state.

Failure policy (per-item AI calls):
    transient → 3 retries with 1s/4s/16s exp backoff
    permanent → no retry; status='failed'
    content   → no retry; status='skipped'
    unknown   → 1 retry; on second failure recorded as 'permanent'

Source-health (separate from item-AI):
    fetch_feed success → reset consecutive_failures, update last_polled_at
    fetch_feed failure → bump consecutive_failures, set last_error_*
"""
from __future__ import annotations

import json
import socket
import sqlite3
import time
import urllib.error
from contextlib import closing
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

from .ai import Summary, summarize
from .db import connect
from .ingest import fetch_feed, insert_new_items

FailureClass = Literal["transient", "permanent", "content", "unknown"]

TRANSIENT_BACKOFF_SECONDS = [1, 4, 16]


@dataclass
class SourceResult:
    source_name: str
    new_items: int = 0
    pending_attempted: int = 0
    processed: int = 0
    failed: int = 0
    skipped: int = 0
    cost_usd: float = 0.0
    fetch_error: str | None = None


@dataclass
class RefreshSummary:
    sources_attempted: int = 0
    sources_failed: int = 0
    items_ingested: int = 0
    items_processed: int = 0
    items_failed: int = 0
    items_skipped: int = 0
    total_cost_usd: float = 0.0
    per_source: list[SourceResult] = field(default_factory=list)


def classify_exception(exc: BaseException) -> FailureClass:
    """Map a raised exception to one of the four failure classes."""
    try:
        import openai
    except ImportError:
        openai = None

    if isinstance(exc, (urllib.error.URLError, socket.timeout, TimeoutError)):
        return "transient"
    if openai is not None:
        if isinstance(exc, openai.RateLimitError):
            return "transient"
        if isinstance(exc, (openai.APIConnectionError, openai.APITimeoutError)):
            return "transient"
        if isinstance(exc, openai.AuthenticationError):
            return "permanent"
    if isinstance(exc, json.JSONDecodeError):
        return "content"
    return "unknown"


def summarize_with_retry(
    content: str,
    why: str,
    title: str,
    model: str | None = None,
) -> Summary:
    """Apply the locked retry policy. Raises the final exception on exhaustion."""
    attempt = 0
    while True:
        try:
            return summarize(content=content, why=why, title=title, model=model)
        except Exception as e:
            cls = classify_exception(e)
            if cls == "transient" and attempt < len(TRANSIENT_BACKOFF_SECONDS):
                time.sleep(TRANSIENT_BACKOFF_SECONDS[attempt])
                attempt += 1
                continue
            if cls == "unknown" and attempt < 1:
                time.sleep(1)
                attempt += 1
                continue
            raise


def persist_summary(conn: sqlite3.Connection, item_id: int, s: Summary) -> None:
    """Single tx: INSERT summaries + INSERT cost_log + UPDATE items.status='processed'."""
    conn.execute(
        """INSERT INTO summaries (
            item_id, relevance_verdict, confidence, relevance_reason,
            content_type_tag, style_tag, purpose, read_time_estimate,
            key_points_json, chapter_index_json, model_used
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            item_id,
            s.relevance_verdict,
            s.confidence,
            s.relevance_reason,
            s.content_type_tag,
            s.style_tag,
            s.purpose,
            s.read_time_estimate,
            json.dumps(s.key_points),
            json.dumps(s.chapter_index) if s.chapter_index else None,
            s.model_used,
        ),
    )
    conn.execute(
        """INSERT INTO cost_log (item_id, model, tokens_in, tokens_out, cost_usd, operation)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (item_id, s.model_used, s.tokens_in, s.tokens_out, s.cost_usd, "summarize"),
    )
    conn.execute(
        "UPDATE items SET status = 'processed' WHERE id = ?",
        (item_id,),
    )
    conn.commit()


def _mark_item_failed(
    conn: sqlite3.Connection,
    item_id: int,
    failure_class: FailureClass,
    message: str,
) -> None:
    status = "skipped" if failure_class == "content" else "failed"
    conn.execute(
        "UPDATE items SET status = ?, failure_class = ?, failure_message = ? WHERE id = ?",
        (status, failure_class, message, item_id),
    )
    conn.commit()


def _update_source_success(conn: sqlite3.Connection, source_id: int) -> None:
    conn.execute(
        """UPDATE sources
           SET last_polled_at = ?,
               consecutive_failures = 0,
               last_error_at = NULL,
               last_error_message = NULL
           WHERE id = ?""",
        (datetime.utcnow().isoformat(timespec="seconds"), source_id),
    )
    conn.commit()


def _update_source_failure(conn: sqlite3.Connection, source_id: int, message: str) -> None:
    conn.execute(
        """UPDATE sources
           SET consecutive_failures = consecutive_failures + 1,
               last_error_at = ?,
               last_error_message = ?
           WHERE id = ?""",
        (datetime.utcnow().isoformat(timespec="seconds"), message, source_id),
    )
    conn.commit()


def _print_item_verbose(item: sqlite3.Row, s: Summary) -> None:
    print(f"--- {item['title'] or '[no title]'} ---")
    print(f"    {item['url']}")
    print(f"    Verdict:    {s.relevance_verdict}  (confidence {s.confidence:.2f})")
    print(f"    Reason:     {s.relevance_reason}")
    print(f"    Type:       {s.content_type_tag}  ·  Style: {s.style_tag}  ·  Read time: {s.read_time_estimate}")
    print(f"    Purpose:    {s.purpose}")
    print(f"    Cost:       ${s.cost_usd:.4f}  (tokens in/out: {s.tokens_in}/{s.tokens_out})")
    print(f"    Key points:")
    for bullet in s.key_points:
        print(f"      • {bullet}")
    print()


def process_source(
    conn: sqlite3.Connection,
    source: sqlite3.Row,
    per_source: int,
    verbose: bool,
    dry_run: bool,
) -> SourceResult:
    """Fetch + ingest + summarize one source. Returns SourceResult; never raises."""
    res = SourceResult(source_name=source["name"])
    if verbose:
        print(f"\n=== {source['name']} ===")
        print(f"URL: {source['url']}")
        print(f"Why: {source['why']}\n")

    try:
        raw_items = fetch_feed(source["url"])
    except Exception as e:
        msg = f"{type(e).__name__}: {e}"
        res.fetch_error = msg
        _update_source_failure(conn, source["id"], msg)
        if verbose:
            print(f"  [feed fetch failed: {msg}]")
        return res

    _update_source_success(conn, source["id"])

    if dry_run:
        existing = {
            row["external_id"]
            for row in conn.execute(
                "SELECT external_id FROM items WHERE source_id = ?",
                (source["id"],),
            )
        }
        new = [it for it in raw_items if it.external_id not in existing]
        res.new_items = len(new)
        if verbose:
            print(f"  [dry-run] {len(new)} new (would skip {len(raw_items) - len(new)} already-known)")
            for it in new[:per_source]:
                print(f"    + {it.title or '[no title]'}")
                print(f"      {it.url}")
        return res

    new_count = insert_new_items(source["id"], raw_items, conn=conn)
    res.new_items = new_count
    if verbose:
        skipped = len(raw_items) - new_count
        if new_count > 0:
            print(f"  [{new_count} new, {skipped} already-known]\n")
        else:
            print(f"  [no new items — feed had {len(raw_items)}, all already-known]\n")

    pending = list(conn.execute(
        """SELECT id, title, url, raw_content FROM items
           WHERE source_id = ? AND status = 'pending'
           ORDER BY id ASC LIMIT ?""",
        (source["id"], per_source),
    ))
    res.pending_attempted = len(pending)

    for item in pending:
        try:
            s = summarize_with_retry(
                content=item["raw_content"] or "",
                why=source["why"],
                title=item["title"] or "",
            )
        except Exception as e:
            cls = classify_exception(e)
            if cls == "unknown":
                cls = "permanent"
            msg = f"{type(e).__name__}: {e}"
            _mark_item_failed(conn, item["id"], cls, msg)
            if cls == "content":
                res.skipped += 1
            else:
                res.failed += 1
            if verbose:
                print(f"--- {item['title'] or '[no title]'} ---")
                print(f"    {item['url']}")
                print(f"    FAILED ({cls}): {msg}\n")
            continue

        persist_summary(conn, item["id"], s)
        res.processed += 1
        res.cost_usd += s.cost_usd
        if verbose:
            _print_item_verbose(item, s)

    return res


def run_refresh(
    per_source: int = 10,
    source_id: int | None = None,
    dry_run: bool = False,
    verbose: bool = True,
) -> RefreshSummary:
    """Top-level entry. Iterates sources, returns RefreshSummary."""
    summary = RefreshSummary()
    with closing(connect()) as conn:
        query = "SELECT * FROM sources"
        params: tuple = ()
        if source_id is not None:
            query += " WHERE id = ?"
            params = (source_id,)
        query += " ORDER BY id"
        sources = list(conn.execute(query, params))

        for src in sources:
            summary.sources_attempted += 1
            res = process_source(
                conn, src,
                per_source=per_source,
                verbose=verbose,
                dry_run=dry_run,
            )
            summary.per_source.append(res)
            if res.fetch_error:
                summary.sources_failed += 1
            summary.items_ingested += res.new_items
            summary.items_processed += res.processed
            summary.items_failed += res.failed
            summary.items_skipped += res.skipped
            summary.total_cost_usd += res.cost_usd

    _print_summary(summary, dry_run=dry_run)
    return summary


def _print_summary(s: RefreshSummary, dry_run: bool) -> None:
    label = "[dry-run] " if dry_run else ""
    print(f"\n=== {label}Refresh summary ===")
    print(f"Sources:    {s.sources_attempted} attempted, {s.sources_failed} failed")
    if dry_run:
        print(f"Would ingest: {s.items_ingested} new items")
        return
    print(f"Ingested:   {s.items_ingested} new items")
    print(f"Processed:  {s.items_processed}")
    print(f"Failed:     {s.items_failed}")
    print(f"Skipped:    {s.items_skipped} (content-class)")
    print(f"Total cost: ${s.total_cost_usd:.4f}")
