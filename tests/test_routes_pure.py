"""Unit tests for the pure helpers in web/routes.py — palette + format + reason-splitter.

These are the trickiest non-DB pieces of view logic: the brittle regex splitter
(flagged in state.md gotchas) and the dispatch maps.
"""
import pytest

from aifeeder.web import routes


# ---------- _palette_for ----------

@pytest.mark.parametrize("tag,expected", [
    ("tutorial", "cool"),
    ("essay", "warm"),
    ("research paper", "cool"),
    ("news", "neutral"),
    ("interview", "warm"),
    ("review", "warm"),
    ("thread", "cool"),
    ("other", "neutral"),
    (None, "neutral"),
    ("unknown_tag_from_drift", "neutral"),  # AI-derived tags can drift; default to neutral
])
def test_palette_for(tag, expected: str) -> None:
    assert routes._palette_for(tag) == expected


# ---------- _format_for ----------

@pytest.mark.parametrize("source_type,expected", [
    ("youtube_channel", "video"),
    ("rss", "reading"),
    (None, "reading"),       # missing source_type falls through to reading
    ("podcast", "reading"),  # future source_type not yet mapped — defaults safely
])
def test_format_for(source_type, expected: str) -> None:
    assert routes._format_for(source_type) == expected


# ---------- _split_reason (the brittle regex splitter) ----------

def test_split_reason_yes_verdict_has_no_caution() -> None:
    """'Yes' reasons don't include 'although'/'but'/'though' — caution stays None."""
    main, caution = routes._split_reason("Worth reading if you care about practical AI engineering.")
    assert main == "Worth reading if you care about practical AI engineering."
    assert caution is None


def test_split_reason_maybe_with_although() -> None:
    main, caution = routes._split_reason(
        "Worth a shot for introspective takes on ADHD although it's mostly lighthearted."
    )
    assert main == "Worth a shot for introspective takes on ADHD"
    assert caution == "although it's mostly lighthearted."


def test_split_reason_maybe_with_but() -> None:
    main, caution = routes._split_reason(
        "Worth a shot for the methodology, but the conclusions are weak."
    )
    assert main == "Worth a shot for the methodology"
    assert caution == "but the conclusions are weak."


def test_split_reason_maybe_with_though_case_insensitive() -> None:
    main, caution = routes._split_reason(
        "Worth a shot for the framing Though the examples felt thin."
    )
    assert main == "Worth a shot for the framing"
    assert caution == "Though the examples felt thin."


def test_split_reason_empty_and_none() -> None:
    assert routes._split_reason(None) == (None, None)
    assert routes._split_reason("") == (None, None)


def test_split_reason_strips_trailing_comma_before_hinge() -> None:
    """The hinge often comes after a comma in AI output; the comma shouldn't stay on the main."""
    main, _ = routes._split_reason("Worth a shot for X, although Y.")
    assert main == "Worth a shot for X"  # no trailing comma
