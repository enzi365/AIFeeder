"""Unit tests for web/writes.py — pure URL-detection + cascade-delete on a tmp DB."""
import sqlite3

import pytest

from aifeeder.web import writes


# ---------- detect_source_type (pure) ----------

@pytest.mark.parametrize("url,expected", [
    ("https://www.youtube.com/@Struthless", "youtube_channel"),
    ("https://youtube.com/channel/UCxxx", "youtube_channel"),
    ("https://youtu.be/abc", "youtube_channel"),
    ("https://m.youtube.com/@foo", "youtube_channel"),
    ("  https://www.youtube.com/@Spaced  ", "youtube_channel"),  # leading/trailing whitespace
    ("https://simonwillison.net/atom/everything/", "rss"),
    ("https://arxiv.org/rss/cs.AI", "rss"),
    ("https://example.com/feed.xml", "rss"),
    ("https://vimeo.com/12345", "rss"),  # vimeo not in the YouTube list
    ("not-a-url", "rss"),  # parse failure falls through to rss
])
def test_detect_source_type(url: str, expected: str) -> None:
    assert writes.detect_source_type(url) == expected


# ---------- delete_source cascade (real tmp SQLite) ----------

def test_delete_source_cascades_to_all_child_tables(tmp_db) -> None:
    """A source with items, summaries, cost_log, and feedback should clear all five
    tables on delete. Order matters: schema has no ON DELETE CASCADE."""
    # Arrange: insert a source + 2 items + 1 summary + 1 cost_log row + 1 feedback row
    with sqlite3.connect(tmp_db) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute(
            "INSERT INTO sources (name, url, source_type, why) VALUES (?, ?, ?, ?)",
            ("CascadeTest", "https://example.com/cascade", "rss", "test cascade"),
        )
        source_id = conn.execute(
            "SELECT id FROM sources WHERE url = 'https://example.com/cascade'"
        ).fetchone()[0]
        for ext_id in ("c1", "c2"):
            conn.execute(
                "INSERT INTO items (source_id, external_id, url, title, raw_content, status) "
                "VALUES (?, ?, ?, ?, ?, 'processed')",
                (source_id, ext_id, f"https://x/{ext_id}", ext_id, "body"),
            )
        item_id = conn.execute(
            "SELECT id FROM items WHERE source_id = ? AND external_id = 'c1'",
            (source_id,),
        ).fetchone()[0]
        conn.execute(
            "INSERT INTO summaries (item_id, relevance_verdict, confidence, relevance_reason, "
            "content_type_tag, style_tag, purpose, read_time_estimate, key_points_json, model_used) "
            "VALUES (?, 'yes', 0.9, 'r', 'other', 'conv', 'p', 'medium', '[]', 'fake')",
            (item_id,),
        )
        conn.execute(
            "INSERT INTO cost_log (item_id, model, tokens_in, tokens_out, cost_usd, operation) "
            "VALUES (?, 'fake', 100, 50, 0.001, 'summarize')",
            (item_id,),
        )
        conn.execute(
            "INSERT INTO feedback (item_id, thumb, reason) VALUES (?, 'up', 'good')",
            (item_id,),
        )
        conn.commit()

    # Act
    deleted = writes.delete_source(source_id)

    # Assert
    assert deleted is True
    with sqlite3.connect(tmp_db) as conn:
        for table, where in [
            ("sources", f"id = {source_id}"),
            ("items", f"source_id = {source_id}"),
            ("summaries", f"item_id = {item_id}"),
            ("cost_log", f"item_id = {item_id}"),
            ("feedback", f"item_id = {item_id}"),
        ]:
            count = conn.execute(f"SELECT COUNT(*) FROM {table} WHERE {where}").fetchone()[0]
            assert count == 0, f"{table} still has rows after delete"


def test_delete_source_returns_false_for_missing(tmp_db) -> None:
    """Defensive: deleting a nonexistent source returns False, not an exception."""
    assert writes.delete_source(99999) is False


def test_insert_source_auto_detects_youtube_type(tmp_db) -> None:
    """URL-detection should set source_type = 'youtube_channel' for YouTube hosts."""
    yt_id = writes.insert_source("YT", "https://www.youtube.com/@Test", "why")
    rss_id = writes.insert_source("RSS", "https://example.com/feed.xml", "why")
    with sqlite3.connect(tmp_db) as conn:
        types = dict(conn.execute(
            "SELECT id, source_type FROM sources WHERE id IN (?, ?)",
            (yt_id, rss_id),
        ).fetchall())
    assert types[yt_id] == "youtube_channel"
    assert types[rss_id] == "rss"
