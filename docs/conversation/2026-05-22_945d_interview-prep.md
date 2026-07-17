# Conversation log — session 945d

_Session ID: 945df053-0fb2-409c-b788-31dbecd1de0a_
_Started: 2026-05-22 (interview-prep turn)_

## 2026-05-22 — Interview prep talking points

**Me:** Read the README and docs/ and help me write answers / talking points for an upcoming interview. The rubric covers technical ability (explain dev process; use AI effectively, responsibly, creatively across diverse tools) and facilitation potential (break vague problems into workable steps for students; guide without doing it for them; guide reflection/adaptation/improvement). Step 3 is training+shadowing TBC — so it's a facilitation/teaching role.

**Claude:** Read README.md + state.md + workflow-notes.md + opening chunks of decisions.md and ideas.md. Produced a structured 5-section prep doc in chat (not a file, per CLAUDE.md's "no docs unless asked" rule), each section anchored to concrete AIFeeder moments rather than generic advice:

- *Technical / dev process:* plan-then-build (the locked 10-step `aifeeder refresh` plan), browser-check loop (the 2×-too-tall home grid fix), per-item commit design. Quantified anchors (43 tests/1.2s, ~$0.0001/RSS item, ~$0.0015/transcript).
- *Technical / AI use:* diverse tools (Claude Code Opus + `/plan-feature` + `Explore` subagent + GPT-4o-mini prod + Anthropic fallback); responsibility encoded as protocol (locked tone phrasings as A-invariants, no-guessing rule, cost transparency); A/B/C split as creative leverage. Highlighted the ingest-flow redirect story (three open Qs = the shape is wrong).
- *Facilitation / break-down:* `/plan-feature` as the literal "vague → workable steps" muscle; A/B/C lens with the "would TikTok do this?" heuristic; reading open questions as a smell.
- *Facilitation / guide-not-do:* `/decide` protocol (pose options + tradeoffs, don't implement); escalation rule; no-guessing-on-ambiguity rule.
- *Facilitation / reflect-adapt:* tutor mode shape (one specific anchored note, save validated approaches too); decisions log + conversation log as reflection scaffolding; README Reflection section as a worked retro example.

Added a quick "stories to keep in back pocket" table mapping 6 build moments to the trait each demonstrates, plus a pre-interview prep tip (skim decisions.md and have 1–2 entries ready to walk through end-to-end). No code changes; no decisions made — pure interview prep, so no entry needed in decisions.md / engineering-decisions.md.
