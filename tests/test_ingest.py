"""Unit tests for ingest._transcript_to_paragraphs — the heuristic chunker
that turns YouTube auto-caption snippets (no semantic breaks) into readable
paragraphs."""
from dataclasses import dataclass

from aifeeder.ingest import _transcript_to_paragraphs


@dataclass
class FakeSnippet:
    """Mirrors the shape of youtube_transcript_api's FetchedTranscriptSnippet
    so we can test the chunker without a network call."""
    text: str
    start: float
    duration: float


def test_chunker_breaks_on_gap_above_threshold() -> None:
    """A > 2.5s pause between snippets should end the current paragraph."""
    snippets = [
        FakeSnippet("First sentence.", start=0.0, duration=2.0),
        FakeSnippet("Second sentence.", start=2.5, duration=2.0),  # no gap, same para
        FakeSnippet("Third sentence after pause.", start=8.0, duration=2.0),  # 3.5s gap
    ]
    result = _transcript_to_paragraphs(snippets, gap_seconds=2.5, max_chars=600)
    paragraphs = result.split("\n\n")
    assert len(paragraphs) == 2
    assert "First sentence." in paragraphs[0] and "Second sentence." in paragraphs[0]
    assert "Third sentence after pause." in paragraphs[1]


def test_chunker_breaks_on_max_chars_at_sentence_boundary() -> None:
    """Once a paragraph exceeds max_chars AND ends on .!?, break before the next snippet."""
    long = "Sentence " + "x " * 200 + "."  # ~400+ chars + ends with period
    snippets = [
        FakeSnippet(long, start=0.0, duration=2.0),
        FakeSnippet("Short next.", start=2.0, duration=1.0),
    ]
    result = _transcript_to_paragraphs(snippets, gap_seconds=10.0, max_chars=100)
    paragraphs = result.split("\n\n")
    assert len(paragraphs) >= 2


def test_chunker_handles_empty_input() -> None:
    assert _transcript_to_paragraphs([]) == ""


def test_chunker_skips_blank_snippets() -> None:
    snippets = [
        FakeSnippet("Real text.", start=0.0, duration=1.0),
        FakeSnippet("", start=1.0, duration=1.0),         # empty — should skip
        FakeSnippet("   ", start=2.0, duration=1.0),      # whitespace — should skip
        FakeSnippet("More text.", start=3.0, duration=1.0),
    ]
    result = _transcript_to_paragraphs(snippets, gap_seconds=10.0, max_chars=600)
    assert "Real text." in result
    assert "More text." in result
