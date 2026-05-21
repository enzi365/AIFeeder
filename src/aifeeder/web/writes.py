"""Real persistent writes from the web layer.

Sibling to:
- `repo.py` — read-only queries
- `fakes.py` — in-memory UI fakes (notes / favourites / highlights) that wipe on reload

Use this module only for writes that need to land in the real schema. Today
that's just source edits (url + why). Future surfaces like delete-source,
archive-item, or mark-read would also land here.
"""
from contextlib import closing

from ..db import connect


def update_source(source_id: int, url: str, why: str) -> bool:
    """Update a source's url + why. Returns True if a row was actually updated."""
    with closing(connect()) as conn:
        cur = conn.execute(
            "UPDATE sources SET url = ?, why = ? WHERE id = ?",
            (url.strip(), why.strip(), source_id),
        )
        conn.commit()
        return cur.rowcount > 0


def insert_source(name: str, url: str, why: str) -> int:
    """Insert a new RSS source. Returns the new source id.

    source_type is hardcoded to 'rss' in v1; the YouTube ingestion path
    ships in phase 4 with its own toggle. Raises sqlite3.IntegrityError
    on duplicate url (UNIQUE constraint) — caller re-renders the modal
    with a friendly message.
    """
    with closing(connect()) as conn:
        cur = conn.execute(
            "INSERT INTO sources (name, url, source_type, why) VALUES (?, ?, 'rss', ?)",
            (name.strip(), url.strip(), why.strip()),
        )
        conn.commit()
        return cur.lastrowid
