"""RSS ingestion. Fetch sources, parse feeds, write new items to DB.

One source failing does not stop others — callers should catch per-source.
For v1 slice: feedparser only; YouTube ingest lands in v2.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass

import feedparser

from .db import connect


@dataclass
class RawItem:
    external_id: str
    url: str
    title: str
    raw_content: str


def fetch_sources(conn: sqlite3.Connection | None = None) -> list[sqlite3.Row]:
    owns = conn is None
    if owns:
        conn = connect()
    try:
        return list(conn.execute("SELECT * FROM sources ORDER BY id"))
    finally:
        if owns:
            conn.close()


def fetch_feed(url: str) -> list[RawItem]:
    """Parse an RSS/Atom feed. Returns normalized items; feedparser is forgiving."""
    feed = feedparser.parse(url)
    items: list[RawItem] = []
    for entry in feed.entries:
        external_id = entry.get("id") or entry.get("guid") or entry.get("link") or ""
        if not external_id:
            continue
        items.append(
            RawItem(
                external_id=external_id,
                url=entry.get("link") or "",
                title=entry.get("title") or "",
                raw_content=entry.get("summary") or entry.get("description") or "",
            )
        )
    return items


def insert_new_items(
    source_id: int,
    items: list[RawItem],
    conn: sqlite3.Connection | None = None,
) -> int:
    """Insert items, deduped by (source_id, external_id). Returns count newly inserted."""
    owns = conn is None
    if owns:
        conn = connect()
    new_count = 0
    try:
        for item in items:
            cursor = conn.execute(
                "INSERT OR IGNORE INTO items "
                "(source_id, external_id, url, title, raw_content) "
                "VALUES (?, ?, ?, ?, ?)",
                (source_id, item.external_id, item.url, item.title, item.raw_content),
            )
            if cursor.rowcount:
                new_count += 1
        conn.commit()
    finally:
        if owns:
            conn.close()
    return new_count
