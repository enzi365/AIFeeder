"""Read-only DB queries for the web layer.

Web layer never writes via the repo — feedback / notes / favourites go through
their own paths (fakes.py for v1; real schema later). Keep repo pure-read.
"""
from contextlib import closing
from typing import Any

from ..db import connect


def get_user() -> dict[str, Any]:
    """Single-user v1: always returns user id 1. See decisions.md → users table."""
    with closing(connect()) as conn:
        row = conn.execute("SELECT id, name FROM users WHERE id = 1").fetchone()
        if row is None:
            return {"id": 1, "name": "you"}
        return dict(row)


def list_sources() -> list[dict[str, Any]]:
    """All sources, alphabetical by name."""
    with closing(connect()) as conn:
        rows = conn.execute(
            "SELECT id, name, url, why FROM sources ORDER BY LOWER(name) ASC"
        ).fetchall()
        return [dict(r) for r in rows]


def get_source(source_id: int) -> dict[str, Any] | None:
    """Single source by id — for the source-edit modal + ingest-panel dispatch."""
    with closing(connect()) as conn:
        row = conn.execute(
            "SELECT id, name, url, why, source_type FROM sources WHERE id = ?",
            (source_id,),
        ).fetchone()
        return dict(row) if row else None


def list_feed_items() -> list[dict[str, Any]]:
    """Items the AI recommended ('yes' or 'maybe'), newest first.

    Joins items + summaries + sources. Returns a flat dict per item with the
    fields the home-page card needs.
    """
    with closing(connect()) as conn:
        rows = conn.execute(
            """
            SELECT
                i.id, i.title, i.url, i.raw_content, i.fetched_at, i.external_id,
                s.relevance_verdict, s.confidence, s.relevance_reason,
                s.content_type_tag, s.style_tag, s.purpose,
                s.read_time_estimate, s.key_points_json,
                src.name AS source_name, src.why AS source_why,
                src.source_type AS source_type
            FROM items i
            JOIN summaries s ON s.item_id = i.id
            JOIN sources src ON src.id = i.source_id
            WHERE s.relevance_verdict IN ('yes', 'maybe')
            ORDER BY i.fetched_at DESC
            """
        ).fetchall()
        return [dict(r) for r in rows]


def get_item(item_id: int) -> dict[str, Any] | None:
    """Full item + summary + source for the content page."""
    with closing(connect()) as conn:
        row = conn.execute(
            """
            SELECT
                i.id, i.title, i.url, i.raw_content, i.fetched_at, i.external_id,
                s.relevance_verdict, s.confidence, s.relevance_reason,
                s.content_type_tag, s.style_tag, s.purpose,
                s.read_time_estimate, s.key_points_json,
                src.name AS source_name, src.why AS source_why,
                src.source_type AS source_type
            FROM items i
            JOIN summaries s ON s.item_id = i.id
            JOIN sources src ON src.id = i.source_id
            WHERE i.id = ?
            """,
            (item_id,),
        ).fetchone()
        return dict(row) if row else None
