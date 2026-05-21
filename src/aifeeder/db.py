"""SQLite connection + schema management. Single-user, local."""
import os
import sqlite3
from pathlib import Path

DB_PATH = Path(os.environ.get("AIFEEDER_DB", "aifeeder.db"))
SCHEMA_PATH = Path(__file__).resolve().parent.parent.parent / "schema.sql"


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def apply_schema(conn: sqlite3.Connection | None = None) -> None:
    """Create tables and seed sources if not present. Idempotent across re-runs."""
    owns = conn is None
    if owns:
        conn = connect()
    try:
        conn.executescript(SCHEMA_PATH.read_text())
        conn.commit()
    finally:
        if owns:
            conn.close()
