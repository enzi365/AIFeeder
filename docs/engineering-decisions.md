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

## ~2026-05-20 — Web stack: Python + FastAPI + HTMX + Jinja2 + SQLite (stdlib)

**My choice:** Python 3.11+ with FastAPI (web framework), HTMX (in-page interactivity), Jinja2 (templates), SQLite via stdlib (DB). No SPA framework, no ORM, no build pipeline.

**Alternatives considered:** Flask + Jinja2 (rejected: FastAPI's lifespan + dependency injection are nicer, no real downside at this scale); Django (rejected: too much for a single-user local app, fights the minimalism); React/Vue/Svelte SPA (rejected: doubles the codebase shape, adds build tooling, mostly ceremony for a server-rendered feed); SQLAlchemy (rejected: 5 tables, single-user, raw SQL is clearer + no migration tooling needed); Litestar / Starlette directly (rejected: FastAPI is the most documented option in the family).

**User response:** silent approval (during initial scoping); reaffirmed during the 2026-05-21 /plan-feature pass when the user asked "what does cheaper mean for HTMX vs SPA" — explanation accepted, no change.

**Refs:** conversation → [2026-05-20_b670.md](conversation/2026-05-20_b670.md) (initial pick); [2026-05-20_b670_ux-design.md](conversation/2026-05-20_b670_ux-design.md) (2026-05-21 /plan-feature confirmation).

---

## 2026-05-21 — /plan-feature open-Q resolutions (cluster of B-decisions)

Six B-category decisions resolved together as part of answering the /plan-feature open questions for the UI build. Bundled under one heading because they came from the same turn and reading them in sequence makes more sense than scattering across the file.

### a. Sample data path: `seed-fake` CLI subcommand

**My choice:** Add an `aifeeder seed-fake` subcommand that inserts ~12 fake items + summaries spanning all 9 content_type_tags. Lets UI dev happen offline + free; runs idempotently.

**Alternatives considered:** Wire `refresh` first (rejected: state.md orders UI before refresh; would cost time + API tokens just to populate dev data); fixtures-on-startup (rejected: would pollute a real DB once refresh lands); hardcoded list in a route (rejected: leaks fixtures into production code path).

**User response:** approved with comment: "confirm". No change.

### b. `users` table — escalated to A (logged in decisions.md)

Originally proposed as a B-choice between hardcoded "Emma", `AIFEEDER_USER` env var, or a `users` table. User pushed back: "don't hardcode. add users table". Escalated B→A because it touches schema shape + forward-compat with the deferred public-distribution work. **Full entry in [decisions.md](decisions.md).** This line is the cross-reference per the CLAUDE.md completeness rule.

### c. Source logo placeholders: monogram circles

**My choice:** Render each source's logo slot as a coloured circle containing the first letter of the source name (e.g. "S" for Simon Willison, "A" for ArXiv). No asset pipeline for v1; real logos can replace these later by swapping a Jinja2 macro.

**Alternatives considered:** Actual logo files (rejected: requires asset pipeline + per-source curation for v1); favicon scraping (rejected: brittle, half the time gives a generic icon, also a privacy leak on each render).

**User response:** approved with comment: "monogram circles".

### d. HTMX for in-page interactions (over vanilla `fetch`)

**My choice:** Use HTMX attributes (`hx-post`, `hx-target`, `hx-swap`) for feedback callouts, note panels, favourite toggles. Server returns HTML partials, HTMX swaps them into the DOM.

**Alternatives considered:** Vanilla `fetch` + manual DOM manipulation (rejected: more JS per interaction, less declarative); Alpine.js as a sidekick (rejected: not needed yet — interactions are simple toggles + server-rendered swaps).

**User response:** approved with comment: "okay i'm not sure what this means so i trust you for the htmx option". Trust-based approval — flagging in case user later finds HTMX awkward and wants to revisit.

### e. CSS Grid `grid-auto-flow: dense` for masonry (over Masonry.js)

**My choice:** Use CSS Grid with `grid-template-columns: repeat(3, 1fr)` + `grid-auto-flow: dense` for the home-page masonry layout. Zero JS dep.

**Alternatives considered:** Masonry.js / Isotope (~30KB JS dep — rejected for v1 but easy retrofit later, the grid container is the only thing that changes); real CSS `grid-template-rows: masonry` (rejected: only in Firefox stable behind a flag as of late 2025 — landing in Safari/Chrome within a year, then this whole question goes away).

**User response:** pushed back with question: "is the 30kb dep really worth the gap thingy? what if i want no gap in the future?" Resolved by clarifying that gaps with `auto-flow: dense` are small not zero, Masonry.js is an easy retrofit if the gaps actually bother her, and real CSS masonry is landing soon. User accepted, didn't change the decision but flagged the retrofit option for later.

### f. Vanilla JS for non-HTMX interactions

**My choice:** Plain `document.querySelector` + `addEventListener` + `classList.toggle` for sidebar collapse, panel slide-in, and the loading-page circle fly-out (~80 LOC total). No framework.

**Alternatives considered:** Alpine.js (~15KB, declarative `x-data` / `x-show` — rejected for v1 because the interactions are all class-toggles, no derived state, no inline editing); React/Vue/Svelte (rejected: massive overkill for ~80 LOC of toggles).

**User response:** pushed back with question: "what does this mean? any long term consequences for this? how does framework help?" Resolved by explaining: vanilla scales fine for toggles + class swaps; Alpine.js becomes worth it if interactions get to "when X changes, Y must update automatically" repeated across many places. User accepted, no change.

**Refs:** conversation → [2026-05-20_b670_ux-design.md](conversation/2026-05-20_b670_ux-design.md) (2026-05-21 17:05 entry — /plan-feature open-Q resolution turn).

---

_Last updated: 2026-05-21 — backfilled stack pick + 6 B-decisions from the /plan-feature open-Q resolution turn. Sets the cadence for going forward per the [completeness rule in CLAUDE.md](../CLAUDE.md#completeness-rule--no-concrete-decision-lives-only-in-conversation)._
