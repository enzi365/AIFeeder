"""Shared test fixtures.

The `tmp_db` fixture monkeypatches `aifeeder.db.DB_PATH` to a temp file so
DB-touching tests don't pollute the real `aifeeder.db`. Schema is applied
fresh per test for isolation.
"""
from pathlib import Path

import pytest

from aifeeder import db


@pytest.fixture
def tmp_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point AIFeeder at a fresh SQLite file with the schema applied."""
    path = tmp_path / "test.db"
    monkeypatch.setattr(db, "DB_PATH", path)
    db.apply_schema()
    return path
