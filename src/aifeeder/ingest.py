"""Ingestion: fetch sources, parse, write new items to DB.

Two source types in narrow phase 4:
- 'rss'             → feedparser on the feed URL
- 'youtube_channel' → yt-dlp enumerates the newest N videos, youtube_transcript_api
                      pulls each video's English auto-captions as raw_content

Videos without an available English transcript are silently dropped at ingest
time — no DB row is created. Rationale: an empty raw_content would summarize
to a low-signal verdict and burn tokens; better to skip until/unless a
transcript exists later. (Same outcome as marking failure_class='content' on
the summarize side, but cleaner at the boundary.)

One source failing does not stop others — callers should catch per-source.
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


def fetch_youtube_channel(url: str, limit: int = 20) -> list[RawItem]:
    """Enumerate newest videos from a YouTube channel + pull each transcript.

    Args:
        url: Channel URL (e.g. https://www.youtube.com/@Struthless or /channel/UCxxx).
             yt-dlp accepts /videos suffix or not — both work.
        limit: max videos to enumerate (newest-first). Bounded again by refresh's
               per_source cap.

    Returns RawItems with raw_content = concatenated transcript text. Videos
    with no transcript available are dropped.
    """
    from yt_dlp import YoutubeDL
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import (
        TranscriptsDisabled,
        NoTranscriptFound,
        VideoUnavailable,
    )

    list_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "skip_download": True,
        "playlistend": limit,
    }
    with YoutubeDL(list_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        entries = info.get("entries") or []

        # Channel-root URLs return a playlist of sub-playlists (Videos / Shorts /
        # Live) instead of a flat video list. Drill into the "Videos" sub-playlist
        # using its canonical /channel/{id}/videos URL.
        if entries and entries[0].get("_type") == "playlist":
            videos_sub = next(
                (e for e in entries if "videos" in (e.get("title") or "").lower()),
                entries[0],
            )
            channel_id = videos_sub.get("id")
            if channel_id:
                sub_url = f"https://www.youtube.com/channel/{channel_id}/videos"
                sub = ydl.extract_info(sub_url, download=False)
                entries = sub.get("entries") or []
    api = YouTubeTranscriptApi()
    items: list[RawItem] = []

    for entry in entries:
        video_id = entry.get("id")
        if not video_id:
            continue
        title = entry.get("title") or ""
        video_url = entry.get("url") or f"https://www.youtube.com/watch?v={video_id}"

        try:
            fetched = api.fetch(video_id, languages=["en", "en-US", "en-GB"])
        except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable):
            continue
        except Exception:
            # Any other transcript error (network blip, regional block, etc.) →
            # skip this video this run; it can be picked up on a later refresh.
            continue

        transcript_text = _transcript_to_paragraphs(fetched)
        if not transcript_text:
            continue

        items.append(RawItem(
            external_id=video_id,
            url=video_url,
            title=title,
            raw_content=transcript_text,
        ))
    return items


def _transcript_to_paragraphs(snippets, gap_seconds: float = 2.5, max_chars: int = 600) -> str:
    """Stitch transcript snippets into paragraphs separated by \\n\\n.

    Break a paragraph when there's either a noticeable pause between snippets
    (> gap_seconds) or the running paragraph has grown beyond max_chars at a
    sentence boundary. This is heuristic but yields readable chunks in the
    content reader without a fancy NLP pass.
    """
    paragraphs: list[str] = []
    current: list[str] = []
    last_end: float | None = None

    for snip in snippets:
        text = (snip.text or "").strip()
        if not text:
            continue
        start = getattr(snip, "start", 0.0) or 0.0
        duration = getattr(snip, "duration", 0.0) or 0.0

        gap = (start - last_end) if last_end is not None else 0.0
        chunk_so_far = " ".join(current)
        ended_sentence = chunk_so_far.endswith((".", "!", "?"))
        too_long = len(chunk_so_far) >= max_chars

        if current and (gap > gap_seconds or (too_long and ended_sentence)):
            paragraphs.append(chunk_so_far)
            current = []

        current.append(text)
        last_end = start + duration

    if current:
        paragraphs.append(" ".join(current))

    return "\n\n".join(paragraphs)


def fetch_for_source(source: sqlite3.Row, limit: int = 20) -> list[RawItem]:
    """Dispatch on source_type. Phase 4 entry point used by refresh."""
    stype = source["source_type"]
    if stype == "youtube_channel":
        return fetch_youtube_channel(source["url"], limit=limit)
    return fetch_feed(source["url"])


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
