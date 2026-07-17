"""Real persistent writes from the web layer.

Sibling to:
- `repo.py` — read-only queries
- `fakes.py` — in-memory UI fakes (notes / favourites / highlights) that wipe on reload

Use this module only for writes that need to land in the real schema. Today
that's source edits + adds. Future surfaces like delete-source, archive-item,
or mark-read would also land here.
"""
from contextlib import closing
from urllib.parse import urlparse

from ..db import connect


# Recognised YouTube hostnames → source_type='youtube_channel'.
# Anything else falls through to 'rss'. URL-detection lets the modal stay
# a single Name/URL/Why form with no extra toggle.
_YOUTUBE_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "youtu.be",
}


def detect_source_type(url: str) -> str:
    """Return 'youtube_channel' for YouTube URLs, 'rss' otherwise."""
    host = (urlparse(url.strip()).hostname or "").lower()
    return "youtube_channel" if host in _YOUTUBE_HOSTS else "rss"


def update_source(source_id: int, url: str, why: str) -> bool:
    """Update a source's url + why. Returns True if a row was actually updated."""
    with closing(connect()) as conn:
        cur = conn.execute(
            "UPDATE sources SET url = ?, why = ? WHERE id = ?",
            (url.strip(), why.strip(), source_id),
        )
        conn.commit()
        return cur.rowcount > 0


def delete_source(source_id: int) -> bool:
    """Hard-delete a source and all its descendants in one transaction.

    Schema has no ON DELETE CASCADE (FKs are enforced but not cascading), so
    children must be deleted bottom-up: feedback → cost_log → summaries → items
    → sources. Returns True if a source row was actually deleted.
    """
    with closing(connect()) as conn:
        # Manual transaction so all five deletes succeed or none do.
        try:
            conn.execute("BEGIN")
            conn.execute(
                "DELETE FROM feedback WHERE item_id IN (SELECT id FROM items WHERE source_id = ?)",
                (source_id,),
            )
            conn.execute(
                "DELETE FROM cost_log WHERE item_id IN (SELECT id FROM items WHERE source_id = ?)",
                (source_id,),
            )
            conn.execute(
                "DELETE FROM summaries WHERE item_id IN (SELECT id FROM items WHERE source_id = ?)",
                (source_id,),
            )
            conn.execute("DELETE FROM items WHERE source_id = ?", (source_id,))
            cur = conn.execute("DELETE FROM sources WHERE id = ?", (source_id,))
            conn.commit()
            return cur.rowcount > 0
        except Exception:
            conn.rollback()
            raise


def insert_source(name: str, url: str, why: str) -> int:
    """Insert a new source. source_type is auto-detected from the URL
    (YouTube hosts → 'youtube_channel', everything else → 'rss').

    Returns the new source id. Raises sqlite3.IntegrityError on duplicate
    url (UNIQUE constraint) — caller re-renders the modal with a friendly
    message.
    """
    url_clean = url.strip()
    source_type = detect_source_type(url_clean)
    with closing(connect()) as conn:
        cur = conn.execute(
            "INSERT INTO sources (name, url, source_type, why) VALUES (?, ?, ?, ?)",
            (name.strip(), url_clean, source_type, why.strip()),
        )
        conn.commit()
        return cur.lastrowid
