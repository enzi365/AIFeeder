"""In-memory stores for notes + favourites (UI-faked v1).

Wiped on uvicorn reload — acceptable for v1 per decisions trail. Real schema
(notes table; favourites store, or extend feedback with thumb='up') lands
when the `refresh` subcommand is wired.
"""
from datetime import datetime
from typing import TypedDict


class Note(TypedDict):
    title: str
    body: str
    created_at: str


_notes: dict[int, list[Note]] = {}
_favourites: set[int] = set()


def get_notes(item_id: int) -> list[Note]:
    return list(_notes.get(item_id, []))


def add_note(item_id: int, title: str, body: str) -> Note:
    note: Note = {
        "title": title,
        "body": body,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    _notes.setdefault(item_id, []).append(note)
    return note


def all_notes() -> list[tuple[int, Note]]:
    """For the sidebar Notes section. Returns (item_id, note) pairs, newest first."""
    flat = [(iid, n) for iid, ns in _notes.items() for n in ns]
    flat.sort(key=lambda x: x[1]["created_at"], reverse=True)
    return flat


def is_favourite(item_id: int) -> bool:
    return item_id in _favourites


def toggle_favourite(item_id: int) -> bool:
    """Returns the new state (True = now-favourited, False = now-unfavourited)."""
    if item_id in _favourites:
        _favourites.remove(item_id)
        return False
    _favourites.add(item_id)
    return True


def all_favourites() -> set[int]:
    return set(_favourites)
