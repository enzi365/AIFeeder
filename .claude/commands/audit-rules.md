---
description: Audit the project's rule files (CLAUDE.md, workflow-notes.md, decisions files) for drift between rules and behaviour
argument-hint: [optional focus — e.g. "decisions logging" or "tutor mode"]
---

Audit the rule-files of this project for **drift between what's written down and what actually happens**. This is different from "is Claude following the rules" — it asks "are the rules I wrote still capturing the behaviour I want?"

If $ARGUMENTS is non-empty, narrow the audit to that focus area. Otherwise, do the full sweep.

## Scope

Read these files (cold — don't rely on memory):

- [`CLAUDE.md`](../../CLAUDE.md) — project rules + tutor mode + pending tutor reminders
- [`docs/workflow-notes.md`](../../docs/workflow-notes.md) — collaboration patterns, A/B/C split, slash-command list, plan-mode notes
- [`docs/decisions.md`](../../docs/decisions.md) — A-category decisions
- [`docs/engineering-decisions.md`](../../docs/engineering-decisions.md) — B-category decisions
- [`docs/state.md`](../../docs/state.md) — current focus (for cross-checking "is this rule still reflected in current state?")

Also skim a recent slice of [`docs/conversation/`](../../docs/conversation/) — the most-recently-modified 2–3 session files — to ground the audit in *actual behaviour* rather than guessing.

## What to look for

Four classes of drift to surface, each with **specific evidence** (file path, line range, conversation entry, or a "this rule has zero entries since YYYY-MM-DD" count):

1. **Rules that don't fire when they should** — the rule is written, but the file/log/artifact it should produce is missing or sparse. Example: "Silent approvals get a short one-line entry too" in [`engineering-decisions.md`](../../docs/engineering-decisions.md) but the file had zero entries for a month. Look for: protocols with empty target files, log conventions producing no logs, escalation rules that never escalated.

2. **Rules that fire too often / noisily** — a rule is producing entries that are mechanical, low-signal, or repetitive. Look for: the same tutor-note pattern firing repeatedly, decisions-file entries that are pure restatements, conversation-log entries that violate the [no-transcripting rule](../../docs/workflow-notes.md). If a rule is consistently producing noise, the rule's threshold or shape is probably wrong.

3. **Rules that exist but lack a corresponding artifact** — the rule says "we do X" but there's no slash-command, hook, file, or skill that operationalises X. Example: "use plan mode for non-trivial changes" with no `/plan-feature` command would be this drift. Look for: imperatives in CLAUDE.md / workflow-notes.md that depend on Claude remembering rather than tooling.

4. **Artifacts that lack a corresponding rule** — the inverse: a file or pattern is being maintained, but no rule mandates it. Means either the rule is implicit (worth writing down) or the file's purpose has drifted (worth re-scoping). Look for: regularly-touched files that aren't referenced in CLAUDE.md's table of artifacts.

## Output shape

A single markdown response with one section per drift class — only include a section if you actually found something for it. Each finding:

- **What:** the specific rule + the specific drift, in one sentence.
- **Evidence:** file path + line numbers, OR the count ("zero entries since 2026-04-01"), OR a conversation excerpt — concrete enough to verify.
- **Suggested fix:** one of — *rewrite the rule*, *add tooling to operationalise it*, *delete the rule*, *delete the artifact*, *raise/lower a threshold*. Brief — the user decides whether to act.

Cap the response at the top 5–7 findings across all classes; rank by leverage (which one, if fixed, would prevent the most future drift). If you find nothing meaningful, say so — empty audits are a real outcome and better than padding.

**Don't fix anything in this command.** Surface the drift; the user decides what to act on. If the user says "go fix X", that's a separate follow-up.

## Self-exclusion

Don't audit *this command file* itself. If `/audit-rules` is producing noise or never finding anything useful, the user will say so directly.
