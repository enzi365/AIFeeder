# Engineering decisions — AIFeeder

B-category decisions: routine engineering choices Claude makes autonomously and briefs the user on. Companion to [`docs/decisions.md`](decisions.md) (which is for A-category — product, mission, architectural, scope).

See [`docs/workflow-notes.md`](workflow-notes.md#design-decision-spectrum-abc-split) for the full A/B/C split and what belongs where.

---

## Logging protocol

**What gets an entry:**
- Every B-category engineering brief — what Claude picked, what alternatives were considered, how the user responded.
- Especially: anything the user pushed back on — what they objected to, how it resolved, the reason.
- Silent approvals get a short one-line entry too — this is the audit trail of *all* engineering choices, not just contested ones.

**What does NOT belong here:**
- A-category decisions (mission, UX, AI behaviour, scope, privacy, cost-vs-quality, content-type handling) — those go in [`docs/decisions.md`](decisions.md).
- C-category execution (naming, formatting, inline helpers) — captured implicitly in git history, not logged anywhere.

**When in doubt — escalate.** If a B-category brief turns out to touch any A-category dimension (mission / UX / AI behaviour / scope / privacy / model placement / cost-vs-quality), pause and let the user choose. Don't pre-commit to an engineering pattern that locks in an A-category answer.

---

## Entry shape

```
## YYYY-MM-DD — [Decision name]

**My choice:** [what + one sentence why]

**Alternatives considered:** [main alternative(s) + why not]

**User response:** silent approval | approved with comment: "..." | pushed back

**(If pushed back) Resolution:** [final answer + reason]

**Refs:** conversation → [...]
```

Append-only, oldest at top, newest at bottom. Don't rewrite past entries — if a B decision later gets revisited or pushed back retroactively, append a new entry that supersedes the old one.

---

_No entries yet — first ones land when the v1 slice build begins. The stack pick (Python + FastAPI + HTMX + Jinja2 + SQLite stdlib) approved during the 2026-05-20 /plan-feature session will be the first entry once it's formally adopted in the scaffold step._
