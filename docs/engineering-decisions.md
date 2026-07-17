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

## 2026-05-21 — UI iteration round 1 (cluster of B-decisions)

Engineering-side resolutions from the first browser-check feedback round. Bundled together because they all came from one user-feedback turn after browsing the rendered UI. The A-category items from the same turn (thumbs supersession, sticky-note → plain block, sans typography, apple verdict indicators, in-text highlighting feature) live in [`decisions.md`](decisions.md).

### a. Sidebar gets a Home nav button (above Library)

**My choice:** Add a Home button + home-icon row above Library / Favourites / Notes. Active-state-aware (`active_page == 'home'`), routes to `/home`.

**Alternatives considered:** Treat the app title / logo as the home affordance (rejected: not discoverable, especially when sidebar is collapsed); rely on browser back-nav (rejected: too easy to get stuck on a content page).

**User response:** approved with comment: "add a home button with a home icon above the library button."

### b. Settings gear icon SVG fix

**My choice:** Replace the existing gear path (which rendered as a malformed blob) with a clean 6-tooth gear path that reads cleanly at 18px.

**Alternatives considered:** Heroicons gear (would require introducing an icon library); Feather gear (same); inline 12-tooth (rejected: too dense at 18px).

**User response:** approved with comment: "the settings gear icon button is a bit misformatted. try again."

### c. Sidebar expand/collapse animation: slow from 400ms to 700ms

**My choice:** Bump `--t-med` (used for the sidebar grid-template-columns transition) from 400ms to ~700ms for the sidebar-specific transition. Keep 400ms as the global default for other transitions; introduce `--t-sidebar` for this one usage.

**Alternatives considered:** Globally slow `--t-med` to 700ms (rejected: would make hover lifts + reveal animations feel laggy); keep at 400ms (rejected: user explicitly flagged it as too fast).

**User response:** approved with comment: "when the sidebar collapses and user presses a button so that it unravels again, make the animation slower because it's too fast right now."

### d. Collapsed-sidebar expand handle (visible tab with `>`)

**My choice:** When sidebar is collapsed, render a small ~24×40 px tab attached to the right edge of the sidebar (or floating off the collapsed sidebar's right border) with a `>` chevron. Click expands the sidebar. Existing chevron button at top of sidebar stays (now redundant when collapsed but useful for keyboard users / when expanded).

**Alternatives considered:** Click-anywhere-on-sidebar-edge to expand (rejected: not discoverable, no visual affordance); keep the top chevron as the only expander (rejected: user explicitly wants a tab affordance).

**User response:** approved with comment: "add a tab also extending out of the sidebar when it is collapsed with a > button to unravel it again."

### e. Avatar SVG fix (silhouette inside the glowing circle)

**My choice:** The current avatar is just a radial-gradient circle with no figure inside (the silhouette layer was collapsed to a pure inset shadow). Add a soft inline silhouette layer (head + shoulders shape) inside the circle so the persona reads as a *figure* not a *coin*. Keep the glow + pulse animation as-is — user explicitly liked those.

**Alternatives considered:** Three.js / Spline embed (rejected: deferred to [ideas.md → 3D glass persona avatar](ideas.md)); Lottie illustration (rejected: asset pipeline + license complications for a v1 polish); flat icon-style avatar (rejected: too clinical, loses the warm radial gradient feel user liked).

**User response:** approved with comment: "the avatar, i like the 3d looking circle right now and even the colour. but the avatar shape is all like collapsed together i think because i just see the circle."

### f. Thought-bubble repositioning (around the head, not over it)

**My choice:** Move the three thought-bubbles from above the avatar to wrap around its top + sides (one upper-left, one upper-right, one upper-centre but higher so it clears the head). Keep the watercolour `mix-blend-mode: multiply` translucency.

**Alternatives considered:** Bubbles only on click instead of hover (rejected: user wants the hover discovery — see ideas.md for click-through to a persona page); bigger bubbles further out (rejected: would clip out of the sidebar width).

**User response:** approved with comment: "the thought bubbles, i like the text within it, but it can be better spaced around the avatar's head because right now it's a bit blocked by the circle."

### g. Card title style: switch from underline-illusion to solid highlight

**My choice:** The current implementation uses `background-image: linear-gradient(transparent 60%, accent 60%)` which renders as a thick underline-ish band on the bottom 40% of the title text. Switch the gradient stop higher (transparent 40%, accent 40%) and saturate the colour slightly so it reads unambiguously as a highlighter strip across the lower half of each title.

**Alternatives considered:** Pure `text-decoration: underline` (rejected: user explicitly said "actually just do highlights instead"); full-text background fill (rejected: too heavy for a list view); margin-on-a-blob box behind text (rejected: would interfere with masonry grid heights).

**User response:** approved with comment: "the underline of the titles are a bit off right now. some look like underline some look like highlights. actually just do highlights instead."

### h. Source Sans 3 added to typography (cross-references decisions.md A-entry)

The font choice itself is in [`decisions.md`](decisions.md) (typography is A-category, mission-aligned). This line is the B-side cross-reference: import via Google Fonts URL alongside the existing Fraunces + Source Serif Pro line; expose as `--font-body-sans: 'Source Sans 3', system-ui, sans-serif;`; apply via class-scoped overrides on `.card .why`, `.card .overlay p / ul`, `.reader p`. Tag pills and "Purpose" / "Key points" headers stay on the existing serif stack.

### i. In-text highlighting feature (cross-references decisions.md A-entry)

The feature scope + in-memory v1 storage is in [`decisions.md`](decisions.md) (B→A escalation). The engineering shape: extend `web/fakes.py` with `highlights: dict[int, list[{quote, note_index}]]`; on render, walk reader paragraphs and substring-match-replace stored quotes with `<mark class="user-highlight">`; client-side, add `.reader` mouseup listener → floating "+ Note" button → opens note panel pre-filled with quote field. After save, client-side wrap the selection in `<mark>` immediately (don't wait for reload).

**Refs:** conversation → [2026-05-20_b670_ux-design.md](conversation/2026-05-20_b670_ux-design.md) (2026-05-21 browser-check feedback turn); decisions.md → 5 A-entries dated 2026-05-21 from the same turn.

---

## 2026-05-21 — Avatar restructure: shaded circle as head + matching shaded body below (supersedes round-1 silhouette-inside-the-circle)

**My choice:** The radial-gradient warm sphere that was acting as the *background* of the avatar (with a dark-brown head+bust silhouette painted *inside* it) is now reframed as the avatar's **head**. A second shaded shape — same warm radial gradient, dome-with-flat-bottom outline — sits below the head with a small (~6–8px) gap as the **body / bust**. The dark-brown silhouette layer added earlier today is removed entirely (`avatar_silhouette` macro deleted from `_icons.html`; `.avatar-silhouette` CSS dropped). Both head + body share the same `pulse-glow` animation so they breathe in sync.

**Alternatives considered:** Keep the silhouette-inside-the-circle approach but make the silhouette more visible (rejected: user explicitly framed the shaded circle as a *head* not a background, so the silhouette was the wrong abstraction — the shaded shape *is* the figure); use an SVG `<defs>` with a radial gradient and fill the bust path with it (rejected: more LOC and indirection than just adding a sibling div with CSS gradient + matching border-radius dome — matches the head's existing pure-CSS approach).

**User response:** approved with comment: "could you keep the circle there as the head of the avatar, then draw the body (same shape as the avatar body you have right now), just make it follow the same style as the shaded circle and place it below it with a gap? then you can remove the avatar icon you have right now because the shaded circle and now the shaded body will be the avatar itself."

**Refs:** engineering-decisions.md → *2026-05-21 UI iteration round 1 cluster › e. Avatar SVG fix* (superseded); conversation → [2026-05-20_b670_ux-design.md](conversation/2026-05-20_b670_ux-design.md) (2026-05-21 second browser-check turn).

---

## 2026-05-21 — Collapsed-sidebar top row: hide gear + avatar-icon + top chevron; move expand-handle to top

**My choice:** When the sidebar is collapsed, only the orange `+` (add source) button stays visible at the top — the **Settings gear**, the **profile / avatar icon**, and the **top chevron-toggle** all `display: none`. The side-tab expand-handle (`.sidebar-expand-handle`) moves from vertical centre (`top: 50%; translateY(-50%)`) to near the top (`top: 0.9rem`, no translate) so it sits at the same vertical line where the top chevron used to be — the handle visually replaces the chevron's role when collapsed.

**Alternatives considered:** Shrink the icons to fit inside the 56px collapsed sidebar (rejected: even at 18px each, four buttons + gaps + the chevron don't fit cleanly in 56px without crowding); keep the side-tab at vertical centre (rejected: user explicitly wants it at the top — also makes UX-sense because the user's eye is already at the top-row icons, expander affordance should be there too); keep gear / profile visible at the top of the collapsed sidebar with a vertical icon stack (rejected: 56px width is too narrow for stacked icons with reasonable hit-targets).

**User response:** approved with comment: "the settings and the avatar ends up leaking out of the sidebar. they don't have to be visible when the sidebar is collapsed, only when it is extended. the > arrow is also leaking out. if you see the > tab closer to the bottom of the screenshot, i want that to be shifted up to where the top > button is."

**Refs:** engineering-decisions.md → *2026-05-21 UI iteration round 1 cluster › d. Collapsed-sidebar expand handle* (refines the position rule); conversation → [2026-05-20_b670_ux-design.md](conversation/2026-05-20_b670_ux-design.md) (2026-05-21 collapsed-sidebar polish turn).

---

## 2026-05-21 — Card title highlight: full-coverage paint (supersedes "raise gradient stop to 40%")

**My choice:** Drop the partial-coverage linear-gradient entirely (`transparent N%, accent N%`) and paint the title's full line-box height with a single solid accent fill. Implementation: `background-image: linear-gradient(accent, accent)` (functionally same as `background-color`, kept as gradient syntax for consistency with the per-palette override pattern). `box-decoration-break: clone` already in place so the highlight re-paints cleanly across wrapped lines.

**Alternatives considered:** Raise the gradient stop further (e.g. to 5–10%, leaving only a sliver of unpainted text on top) — rejected: still keeps the "asymmetric band" feel that the user identified as the underlying problem; **soft watercolor edges** via multi-stop gradient with fade-in/out top + bottom (deferred: would require RGB-broken-out palette vars; not worth the refactor unless user asks for softer edges).

**User response:** approved with comment: "see that the highlight of the title of each content block is not really aligned? i realised it's aligned to the bottom of the text because originally it was meant to be an underline. change that and make it behave like an actual highlight."

**Refs:** engineering-decisions.md → *2026-05-21 UI iteration round 1 cluster › g. Card title style* (superseded — the bottom-anchored band approach was the root cause; full-coverage paint replaces it); conversation → [2026-05-20_b670_ux-design.md](conversation/2026-05-20_b670_ux-design.md) (2026-05-21 third browser-check turn).

---

## 2026-05-21 — Card title highlight: per-line bands with transparent top + bottom margins (supersedes "full-coverage paint")

**My choice:** Title background uses a gradient with **transparent top + bottom margins** so each wrapped line's highlight is visibly distinct from the next: `linear-gradient(transparent 12%, accent 12%, accent 88%, transparent 88%)`. Combined with the existing `display: inline` + `box-decoration-break: clone`, each line-fragment renders its own band sized to that line's actual text width (line 1 wide, line 2 narrow → L-shape, not merged rectangle). Highlight covers the middle ~76% of line-height, comfortably covering x-height + most of cap-height while leaving ~3px transparent on each side of the line-box.

**Alternatives considered:** Increase title `line-height` to add vertical gap between full-coverage highlights (rejected: would visibly loosen the title block — at 1.15rem + 1.3 line-height the title already feels right, the issue is *the highlight touching*, not the typography); use `background-color` instead of `linear-gradient` for the painted region (rejected: kept gradient syntax for the per-palette override pattern consistency, and gradients give us the transparent-margin lever without touching typography).

**User response:** approved with comment: "i don't like how block it is now. it's a square. if the text has 2 lines, i want there to be a highlight for each line, and wrapped around the text. as of now, if the first line is longer and the second is shorter, the box just highlights the width of the context block and the height is just how many lines."

**Refs:** engineering-decisions.md → *2026-05-21 — Card title highlight: full-coverage paint* (superseded — full-coverage caused adjacent-line highlights to touch and merge visually); conversation → [2026-05-20_b670_ux-design.md](conversation/2026-05-20_b670_ux-design.md) (2026-05-21 fourth browser-check turn).

---

## 2026-05-21 — Source-edit modal (cluster of B-decisions)

Engineering-side choices supporting the new source-edit feature. The A-side ("sources are editable from the UI") lives in [decisions.md](decisions.md). This cluster covers the implementation shape.

### a. New `web/writes.py` module (instead of extending `repo.py`)

**My choice:** Real persistent writes from the web layer go in a new `web/writes.py` module. `repo.py` keeps its read-only docstring intact. `fakes.py` keeps its in-memory-fake docstring intact. Three modules now own three different write postures: `repo` (reads), `fakes` (in-memory fakes — notes/favourites/highlights), `writes` (real DB writes from UI — source edits today; future archive/delete/etc).

**Alternatives considered:** Extend `repo.py` with a writes section + update its docstring (rejected: muddies the read-only invariant — easier to keep the file pure and add a sibling module); put source writes in `fakes.py` (rejected: not a fake, persists to real schema); skip the module and inline the SQL in the route handler (rejected: route handlers should stay thin and the SQL belongs near the connection-management code).

**User response:** silent approval (chose persist over stub via AskUserQuestion).

### b. Source-edit modal pattern: backdrop blur, centered card, HTMX-driven open + close-on-multiple

**My choice:** Modal opens via HTMX GET `/sources/{id}/edit` → renders `partials/source_modal.html` into a `<div id="modal-slot">` placed once in [base.html](../src/aifeeder/templates/base.html) (available globally). Backdrop is fixed-inset full-viewport with `backdrop-filter: blur(6px)` + semi-transparent overlay. Sidebar's `z-index: 250` keeps it above the backdrop's `z-index: 200` so it stays sharp + interactive per the user's brief; modal card has `z-index: 300`. Close on: Cancel button, Esc key, click on backdrop (outside the modal card) — all clear `#modal-slot`. Save: POST `/sources/{id}` → returns `204 + HX-Refresh: true` so the page reloads with the updated source name/url/why everywhere (sidebar, future references). Same `HX-Refresh: true` pattern as the quote-attached note save from earlier today — consistent in-house convention.

**Alternatives considered:** Modal positioned inside the main column (offset right by sidebar width) instead of viewport-centered (rejected: complicates collapsed-sidebar case where offset would be wrong; viewport-centered is simpler and visually fine because the sidebar is left-flush); HTMX swap the sidebar source-row in place instead of full reload (rejected: re-rendering just the sidebar is fragile because the row's monogram, the active-state, and the future per-source counts would all need targeted swaps — full reload is cheaper and idempotent); modal mounted per-page instead of in `base.html` (rejected: every page would need to repeat the slot div).

**User response:** approved with comment: "when user click a source on the sidebar, a block will appear on the center of the page blurring everything around it except the sidebar."

### c. Why-textarea copy: helper hint *above* the field, not a placeholder

**My choice:** Single textarea with a small italic helper line *above* the field: "What do you value from this source? What would you rather not receive?" — stays visible even after the user starts typing. Field placeholder stays empty so the user sees an unmarked writing surface as they think.

**Alternatives considered:** Two-question placeholder inside the textarea (rejected: disappears the moment user types — they lose the cognitive scaffold mid-sentence); two separate textareas joined into one `why` string on save (rejected: more friction, and the `sources.why` column is a single TEXT field — splitting + joining is a code smell when the storage is unsplit).

**User response:** approved via AskUserQuestion (option C from a 3-option set).

### d. Sidebar source-row becomes HTMX-trigger (not `<a href="#">` placeholder)

**My choice:** Source-row tag stays `<a>` for keyboard-tab semantics but drops `href="#"` (the dead anchor) and uses `hx-get="/sources/{id}/edit" hx-target="#modal-slot" hx-swap="innerHTML"`. Adds `style="cursor: pointer;"` to keep the click affordance now that `href` is gone (an alternative was `role="button" tabindex="0"` — kept simpler; HTMX handles the click + keyboard activation reasonably).

**Alternatives considered:** Use `<button>` instead of `<a>` (rejected: would lose the visual treatment from `.source-row` styling that's tuned for anchor display + would need to reset button defaults).

**User response:** silent approval (implicit in the source-click-to-edit ask).

### e. Repo gets a small `get_source(id)` lookup for the edit endpoint

**My choice:** Added a tiny `get_source(id) -> dict | None` query to `repo.py` (parallel to the existing `get_item`). The modal needs to render with the current url + why pre-populated; the existing `list_sources()` returns all sources so could be filtered in-route, but a direct id lookup is cleaner.

**Alternatives considered:** Filter the result of `list_sources()` in the route (rejected: O(n) for no reason, and inconsistent with the existing `get_item` pattern).

**User response:** silent approval (implementation detail).

### f. Graceful duplicate-URL handling: re-render modal with `.modal-error` (not 500)

**My choice:** `sources.url` carries a `UNIQUE` constraint (per the original schema). When the user edits a source's URL to one already held by another source, the `UPDATE` raises `sqlite3.IntegrityError`. Wrap `writes.update_source` in `try/except IntegrityError`; on the error path, return a 200 re-rendering `partials/source_modal.html` with the user's typed values preserved (so they don't have to re-type) + an `error` variable set to "That URL is already used by another source. Pick a different one." The modal partial conditionally renders `<div class="modal-error">...</div>` above the form, styled with a soft red palette tone (`#FBE7E2` / `#E5A99B` / `#6B2A1E`) so it reads as a gentle correction rather than a system error.

**Alternatives considered:** Return 400 + raw error message (rejected: HTMX's default behaviour doesn't swap on non-2xx, would need `HX-Reswap` header — more moving parts for the same UX); validate URL uniqueness client-side via a HEAD probe (rejected: race condition between probe and submit + adds JS for a corner case); change the schema to allow duplicate URLs (rejected: URL uniqueness is correct — two different sources shouldn't both point at the same RSS feed, that's a data-quality issue worth catching).

**Discovered during smoke-testing.** During end-to-end testing the route returned 500 on the duplicate-URL path. Surfaced this as a real UX failure (also discovered that a prior test pollution created a duplicate Simon Willison row at id=89, cleaned up: `DELETE FROM sources WHERE id = 89; UPDATE sources SET url = '...atom/everything/' WHERE id = 1`). The integrity-error handling is the durable fix; the cleanup was a one-time local-DB hygiene step.

**User response:** silent approval (defensive engineering, no user friction).

**Refs:** decisions.md → *2026-05-21 — Sources are user-editable from the UI* (the A side of this feature); conversation → [2026-05-20_b670_ux-design.md](conversation/2026-05-20_b670_ux-design.md) (2026-05-21 source-edit modal turn).

---

_Last updated: 2026-05-21 — Source-edit modal cluster (6 B-decisions supporting the A-decision in decisions.md: new `writes.py` module, modal pattern + HX-Refresh save, helper-hint copy choice, sidebar source-row HTMX wiring, `get_source` repo lookup, graceful duplicate-URL handling via `.modal-error` re-render)._

---

## 2026-05-22 — `aifeeder refresh` plan-feature open-Q resolutions (cluster)

Resolved during `/plan-feature wire refresh subcommand`. User agreed to all 5 architectural tradeoffs (1 wholesale approval) and answered 7 open questions; compact cluster below. Implementation has not started — these lock the shape before code lands.

### Architectural tradeoffs (approved wholesale)

- **a. Per-item commit boundary, not per-source batch.** A crash mid-source must not waste already-paid AI calls. Disk I/O is cheap vs. summarization cost.
- **b. Within-one-run retry scope.** Transient retries (3x, 1s/4s/16s exp backoff) happen inside a single `refresh` invocation only — no `retry_count` / `next_retry_at` columns. Cost: a yesterday-transient item is silently re-retried tomorrow as fresh. Acceptable in v1; revisit if a source goes flaky for days.
- **c. Writes live in `refresh.py`, not a shared `aifeeder/writes.py`.** Keeps the web-side / CLI-side split explicit (`web/writes.py` is web-only; `refresh.py` is CLI-only). Promote to a shared module only when a third write surface appears (e.g. scheduler).
- **d. Failure classification by exception type, not by adapting `ai.py`.** Pragmatic lookup table (`urllib.error.URLError` / `socket.timeout` / `openai.RateLimitError` → transient; `openai.AuthenticationError` → permanent; `json.JSONDecodeError` → content; default → unknown). Couples `refresh.py` to provider exception names; revisit when Anthropic provider is wired.
- **e. No periodic/cron refresh in v1 — manual CLI only.** Mission-aligned: doomscrolling-replacement actively wants manual cadence, not push.

### Open-question answers

1. **Notes / favourites / highlights migration — deferred to YouTube session.** Stays in `web/fakes.py` as in-memory dicts. `refresh` only inserts new items + summaries; doesn't touch the fake stores (they're keyed by item_id; new items just have no notes/favs until added).
2. **Default `--per-source` cap = 10.** First-run backlog protection. Override via `--per-source N`.
3. **Cost reporting: console only, not UI.** Each `refresh` prints per-item cost + per-source subtotal + total. `cost_log` rows are written for future analysis; no UI dashboard in v1. **Refs:** state.md → *Out of v1: cost dashboard*.
4. **Don't preserve `seed-fake` items alongside real items.** When `refresh` lands, expected flow is: delete the DB, re-`init`, run `refresh` for real data. No co-existence with fakes. Will document the reset workflow in state.md when implementation lands.
5. **`consecutive_failures` resets on source-fetch success, not per-item AI success.** The `!` icon indicates source health (feed unreachable), not summarization health (an AI rate-limit shouldn't mask a healthy source).
6. **`--dry-run` kept.** Fetches + parses feeds + shows what *would* be ingested, but doesn't insert items, doesn't call AI, doesn't write to DB. Use case: debugging "why didn't `refresh` pick up that Simon post" without paying AI cost.
7. **Verbose by default + `--quiet` flag** *(supersedes my initial recommendation of the opposite default).* `aifeeder refresh` prints full preview-style 12-line detail per item by default (verdict, confidence, reason, type/style/read-time, purpose, cost, key points). `--quiet` drops to one-line-per-item + per-source subtotal. Rationale: user wants the AI's full reasoning visible at the moment of ingestion, not buried behind a flag — the noisy default is mission-aligned (mindful consumption *includes* understanding why an item was filtered in/out).

### Scope ordering (post-refresh phase plan)

- **Phase order after `refresh` lands:** real-world test → fix top 1-2 issues → **source-add UI** (reuses source-edit modal pattern with empty fields; orange `+` button currently no-op) → YouTube/Struthless + notes/favs/highlights schema migration. Source-add UI was previously *unscheduled*; user explicitly slotted it before YouTube this turn.

**User response:** explicit approval to all 5 tradeoffs + 7 open-Q answers (interactive `AskUserQuestion` used for #7 to disambiguate "preview style" wording). #7 specifically reversed my initial recommendation — user wants verbose default.

**Refs:** conversation → [2026-05-20_b670_ux-design.md](conversation/2026-05-20_b670_ux-design.md) (2026-05-22 `/plan-feature` turn); state.md → *Next steps* (will reorder when implementation lands); decisions.md → *2026-05-21 — Sources are user-editable from the UI* (open follow-on (a) re. add-source modal pattern reuse is now scheduled).

---

_Last updated: 2026-05-22 — `aifeeder refresh` plan-feature open-Q resolutions cluster (5 tradeoffs + 7 open-Q answers + post-refresh scope ordering). No code yet — locks the shape before implementation starts._

---

## 2026-05-22 — `aifeeder refresh` implementation shipped (small follow-on choices)

The 10-step plan above landed in `src/aifeeder/refresh.py` + `src/aifeeder/cli.py`. Smoke-test result: 4 items processed across 2 sources at $0.0015 total, dedup verified two ways (insert-side via `--dry-run` showing 490 already-known; summarize-side via re-run picking 2 fresh pending items rather than re-summarizing). UI integration confirmed by curling `/home` — all 3 feed-eligible real items render with locked tone phrasings ("Skip — this focuses…", "Worth a shot for X although Y").

A handful of micro-choices made during implementation that weren't pre-specified:

- **Transient lookup extended to `openai.APIConnectionError` and `openai.APITimeoutError`.** Plan only listed `RateLimitError` + non-OpenAI URLError/socket.timeout under transient; the two OpenAI network classes are obviously transient and the SDK raises them on flaky connections / read timeouts. Adding them costs nothing and prevents silently turning a network blip into a permanent failure.
- **`process_source` documented as "never raises" — all per-source exceptions caught.** The plan implied this (return a `SourceResult` per source) but didn't spell out the contract. Locking it in the docstring so a future caller can rely on it for the for-loop in `run_refresh`.
- **DB hygiene: moved `aifeeder.db` → `aifeeder.db.seedfake.bak` instead of `rm`.** The locked plan said "delete DB + re-init"; chose backup-rather-than-delete for the smoke-test transition so the seed-fake state stays inspectable. One-line operational deviation, not a re-decision — `rm aifeeder.db.seedfake.bak` is fine whenever.
- **Timestamps use Python-side `datetime.utcnow().isoformat(timespec="seconds")` rather than SQL `CURRENT_TIMESTAMP`.** Matches the format that schema's `TIMESTAMP DEFAULT CURRENT_TIMESTAMP` produces ('YYYY-MM-DDTHH:MM:SS'). Mostly cosmetic — either would work — but Python-side avoids a second round-trip when bundling multiple updates.

**User response:** pending (just shipped; will surface in next browser-check / push round).

**Refs:** conversation → [2026-05-20_b670_ux-design.md](conversation/2026-05-20_b670_ux-design.md) (2026-05-22 implementation turn); plan-cluster above (same file, prior H2).

---

_Last updated: 2026-05-22 — `aifeeder refresh` shipped. App now runs on real persisted RSS data; UI integration confirmed via /home curl. Seed-fake DB backed up to `aifeeder.db.seedfake.bak`._

---

## 2026-05-22 — Source-add UI shipped (orange `+` button now functional)

Phase-3 work from the locked post-refresh order: wired the sidebar `+` button to a real DB-write flow, mirroring the source-edit pattern. New `insert_source(name, url, why)` in [web/writes.py](../src/aifeeder/web/writes.py); two new routes `GET /sources/new` + `POST /sources` in [web/routes.py](../src/aifeeder/web/routes.py); the existing [partials/source_modal.html](../src/aifeeder/templates/partials/source_modal.html) was extended (one shared template) to render in add-mode when `source.id` is falsy. Smoke-tested end-to-end via curl — all five paths green (GET new modal, POST empty → modal-error, POST duplicate URL → modal-error, POST valid → 204 + HX-Refresh:true with row created, GET edit unchanged).

Small choices made during implementation:

- **One shared modal template** (not a separate `source_add_modal.html`). Why: avoids drift between two markup blocks that are 90% identical. Cost: a couple `{% if is_add %}` branches in the template. Set `is_add = not source.id` at the top so the branches read cleanly.
- **`source_type` hardcoded to `'rss'`** in `insert_source`. Why: YouTube ingestion ships in phase 4 with its own pipeline; adding a no-op `<select>` now is premature UI. When YouTube lands, the toggle goes in alongside the yt-dlp work.
- **All three fields required, one generic modal-error.** Server-side: trim then check non-empty before touching the DB. Client-side: HTML5 `required` for per-field UX (browser hints which field is missing before submit). The generic "All fields are required." server error covers the JS-disabled case + paranoia.
- **Field order: Name → URL → Why** (reading order for a new thing). The edit modal hides Name (it's already in the H2 title), so this is the first time the input appears anywhere in the UI.
- **Route ordering**: literal `POST /sources` registered BEFORE `POST /sources/{source_id}` per the Starlette route-order gotcha already documented in state.md. Same precaution for `GET /sources/new` vs `GET /sources/{source_id}/edit` — different shapes, but registered first defensively.
- **Success behavior: `HX-Refresh: true`** (matches the edit pattern). Why: the new source needs to appear in the sidebar source-list immediately. A full reload is the simplest correct answer; partial-swap into the sidebar would couple this route to the sidebar template.

**User response:** pending (will surface in next browser-check round).

**Refs:** conversation → [2026-05-20_b670_ux-design.md](conversation/2026-05-20_b670_ux-design.md) (2026-05-22 source-add UI turn); decisions.md → *2026-05-21 — Sources are user-editable from the UI* (open follow-on (a) — add-source modal pattern reuse — now resolved by this entry).

---

_Last updated: 2026-05-22 — Source-add UI shipped. Phase 3 of the locked post-refresh order complete. Next: real-world test + phase 4 (YouTube/Struthless)._

---

## 2026-05-22 — Phase 4 narrow shipped (YouTube ingestion via yt-dlp + youtube-transcript-api)

Narrow phase 4 from the locked post-refresh order: end-to-end YouTube channel ingestion. New [ingest.fetch_youtube_channel()](../src/aifeeder/ingest.py) enumerates channel videos via yt-dlp, pulls each transcript via youtube-transcript-api, chunks snippets into pseudo-paragraphs, returns `RawItem`s. New `fetch_for_source(source)` dispatcher in the same module branches on `source_type`. [refresh.py:209](../src/aifeeder/refresh.py#L209) now calls the dispatcher instead of `fetch_feed` directly. URL-detection in [web/writes.py.insert_source()](../src/aifeeder/web/writes.py) auto-sets `source_type='youtube_channel'` for youtube.com / youtu.be / m.youtube.com / www.youtube.com hosts — modal stays a single Name/URL/Why form with no toggle. Smoke-tested end-to-end on Struthless: 3 videos fetched, 3 verdicts at $0.0036 total (~12x cost of an RSS item — long transcripts are the cost driver), all three locked tone phrasings present ("Worth reading if…", "Worth a shot for X although Y", "Skip — this is mostly Z"), content page renders transcripts as 38–42 paragraphs.

User confirmed two A-dimensions in advance via [`AskUserQuestion`](conversation/2026-05-22_4dac.md): (1) narrow scope (vs full); (2) same tone phrasings as RSS (vs separate "Worth watching" variant).

Engineering choices made during implementation:

- **`youtube-transcript-api` for transcripts, yt-dlp for channel enumeration** — two deps, but yt-dlp's automatic_captions URLs return rolling auto-caption JSON3/VTT that needs ~50 lines of fragile dedup logic. youtube-transcript-api (~50KB) hits YouTube's transcript endpoint directly and returns clean text in one call.
- **URL-detection over an explicit `<select>` toggle** in the add-source modal. youtube.com / youtu.be / etc. hosts → `youtube_channel`; everything else → `rss`. Zero template change. If detection misfires on a real channel URL we'll add the toggle in phase-4-full.
- **Channel-root URL drill-through.** Hitting `youtube.com/@Handle` returns a playlist of sub-playlists (Videos / Shorts / Live) rather than flat videos. The function detects `entries[0]._type == 'playlist'`, finds the sub-playlist whose title contains "videos", and re-extracts using `channel/{channel_id}/videos`. Tested with `/@Struthless` — works.
- **Pseudo-paragraph chunking via `_transcript_to_paragraphs()`.** Auto-caption snippets are ~3–5 second chunks with no semantic breaks; rendering as one `<p>` is unreadable. Heuristic: split on either a > 2.5s gap between snippets OR a sentence boundary after the running chunk hits 600 chars. Result on Struthless: 36k-char transcript → 38 paragraphs averaging ~950 chars. Not perfect (auto-caption `>>` speaker markers leak through; some sentences split awkwardly) but dramatically better than a single blob. Phase-4-full could replace this with a smarter pass.
- **Silent-skip videos without transcripts.** `TranscriptsDisabled` / `NoTranscriptFound` / `VideoUnavailable` from `youtube_transcript_api._errors` → continue the loop, no DB row created. Alternative was insert-with-empty-`raw_content` and let `summarize` mark `failure_class='content'` — would burn tokens for poor signal and clutter the DB.
- **`per_source` cap doubles as the YouTube enumeration `limit`.** No separate YT cap — `fetch_for_source(source, limit=per_source)` plumbs through. So `aifeeder refresh --source-id N --per-source 3` enumerates exactly 3 videos, no waste.

Known papercut to surface in state.md: yt-dlp first-fetch latency on a channel with ~100 videos is 30–60s (it's network-bound, not parallelizable trivially); a YT-heavy refresh will be noticeably slower than the all-RSS path.

**User response:** pending (will surface on next browser-check / real-world-use round).

**Refs:** conversation → [2026-05-20_b670_ux-design.md](conversation/2026-05-20_b670_ux-design.md) (2026-05-22 phase-4-narrow turn); state.md → *Next steps* (phase 4 narrow done; phase-4-full + real-world test now next); decisions.md → no new A-entry (the two A-dimensions resolved in `AskUserQuestion` confirmed pre-existing direction; "same tone as RSS" is consistent with the 2026-05-20 AI tone lock).

---

_Last updated: 2026-05-22 — Phase 4 narrow shipped. YouTube ingestion working end-to-end on Struthless at $0.0036/3 videos with locked AI tone preserved. Next: phase-4-full (iframe + chapters + real notes/favs schema) and/or real-world test._

---

## 2026-05-22 — Content-page iframe + home-card format icons

User asked "how fast to add the youtube thumbnail and the iframe in the content blocks" — I flagged that **YT thumbnails on home cards is an A-reconsider** (decided against in 2026-05-21 per mindfulness paradox) and recommended shipping the iframe (already A-locked per 2026-05-20) and pausing on thumbnails. User confirmed: **no thumbnails**, **iframe in content block**, plus a third ask — **coloured SVG format-type icons** (video / audio / reading) next to the apple on home cards, picked from content format.

Built end-to-end. Six engineering choices:

- **Format dispatch from `source_type`, not `content_type_tag`.** source_type is structurally known (set by URL detection at ingest time); content_type_tag is AI-derived and drifts (the Struthless smoke test produced 'video', 'essay', and 'other' tags across three videos from the same channel). Mapping in [routes.py `_SOURCE_TYPE_TO_FORMAT`](../src/aifeeder/web/routes.py): `youtube_channel`→video; `rss`→reading; future `podcast`→audio. The 'audio' icon ships now even with no audio source defined — keeps the trio coherent.
- **video_id derived from external_id (no schema change).** YouTube's `external_id` IS the video_id (set in [ingest.fetch_youtube_channel](../src/aifeeder/ingest.py)), so iframe URL construction is `https://www.youtube-nocookie.com/embed/{external_id}` — no new column needed. Added `i.external_id` + `src.source_type` to both [repo.py queries](../src/aifeeder/web/repo.py); `_enrich_item` exposes a typed `video_id` field that's `None` for non-YT items so the template can gate on truthiness.
- **`youtube-nocookie.com` privacy-mode embeds.** Fits the mindfulness positioning — no tracking cookies, cleaner default. End-screen recommendations still appear at video end (no way to fully disable without paid Premium API); not worth gold-plating today.
- **No autoplay.** Autoplay = TikTok-paradox red flag. iframe loads paused. User has to choose to start.
- **iframe ABOVE the transcript, both visible.** Transcript stays scannable + searchable + note-attachable; iframe is for when you actually want to watch. Replaces neither. **Update (same day):** user asked to move the iframe *below* the purpose + key-points callout — same intent (iframe + transcript both visible) but reading order now: title → source-line → callout (the AI's pre-watch context: "is this worth my time?") → iframe (decide to watch) → transcript. Matches the mindfulness flow: pre-frame before press play.
- **Format icon sits LEFT of the apple, smaller (22px vs 30px), slightly faded (0.85 opacity).** Apple is the verdict (foreground decision), format icon is metadata (background info). Hover bumps both to full opacity. Colors: video → `--accent-cool` (teal, "watch" = focused activity); audio → `--accent-warm` (sienna, "listen" = warm/ambient); reading → `--ink-soft` (muted brown, "read" = paper).

Smoke test on running server: home page rendered 17 reading icons + 3 video icons (= 17 RSS items + 3 Struthless videos — correct distribution); YT content page (item 1476) rendered iframe with the right video_id (`j-TK_oWSg0g`) via `youtube-nocookie.com/embed/`; RSS content page (item 9) rendered zero iframes (correct gating on `item.video_id`).

**User response:** pending (needs browser-check — particularly the icon color/sizing balance vs the apple).

**Refs:** conversation → [2026-05-20_b670_ux-design.md](conversation/2026-05-20_b670_ux-design.md) (2026-05-22 iframe + format-icons turn); decisions.md → *2026-05-20 — YouTube playback iframe* (already-A-locked, executed today); decisions.md → *2026-05-21 — no thumbnails in v1* (still standing — thumbnails NOT added, mindfulness paradox preserved).

---

_Last updated: 2026-05-22 — Content-page iframe + home-card format icons shipped. YT videos now embed via youtube-nocookie.com; home cards show video/audio/reading icon next to apple based on source_type._

---

## 2026-05-22 — Home cards size to content (drop fixed row height + shape-text row span)

User browser-checked the home grid post-format-icons and flagged that research-paper / essay cards (blue) were ~2x taller than their content needed, while the brown maybe-cards fit tightly. Root cause: [cards.css](../src/aifeeder/static/css/cards.css) had `grid-auto-rows: 220px` (fixed) + `.shape-text { grid-row: span 2 }` applied to `'research paper'` and `'essay'` content-type tags via [routes.py `_shape_for`](../src/aifeeder/web/routes.py), forcing those cards to 440px regardless of actual text length.

**My choice:** `grid-auto-rows: auto` (rows size to tallest card in the row) + drop `.shape-text` row-span entirely + add `min-height: 180px` floor on `.card` (so very-short cards don't look squished). Kept `.card.shape-video { grid-column: span 2 }` for future video/interview items (wider, not taller). Kept `.shape-text .title { font-size: 1.3rem }` since the title-size bump on research-papers/essays is a visual-emphasis concern decoupled from card height — `_shape_for` still returns `'text'` for those tags, so the class is still in the DOM and the larger title still renders.

**Alternatives considered:** (1) True per-card masonry — would need CSS columns (breaks left-to-right chronological reading order) or a JS lib (overkill for the current asymmetry). (2) Keep fixed-height rows but make shape-text dynamic from content length — adds complexity, less honest than just letting the grid breathe. (3) Cap with `max-height` on cards — would clip long reasons; the reason content is what makes a card worth rendering.

**Tradeoff:** within a single row, cards still stretch to match the tallest card in that row (CSS Grid behavior). Across rows, heights vary. This isn't true masonry — if a row has one tall card and one short card, the short card still has trailing whitespace below its content. The 180px floor + most cards being similar-content-length should keep this from being visually loud; if it becomes a problem we'd need JS masonry.

**User response:** pending (will surface on next browser-check).

**Refs:** conversation → [2026-05-20_b670_ux-design.md](conversation/2026-05-20_b670_ux-design.md) (2026-05-22 card-sizing turn).

---

_Last updated: 2026-05-22 — Home cards now size to content. Fixed 220px row height dropped; `.shape-text` row-span gone. Research-paper / essay cards no longer 2x too tall._

---

## 2026-05-22 — Source-add ingest panel implementation

A-shape locked in [decisions.md → 2026-05-22 Source-add ingest flow](decisions.md). Implementation choices:

- **`POST /sources` success now returns the ingest panel** (not HX-Refresh:true). Instead of reloading immediately after creating the source, the response renders [partials/ingest_panel.html](../src/aifeeder/templates/partials/ingest_panel.html) into the same `#modal-slot` — preserves the modal's spatial continuity (user doesn't lose their cursor / context). The reload moves to the close-of-ingest-flow instead.
- **`data-modal-needs-reload` marker on the modal backdrop.** The X / Esc / backdrop-click / Cancel buttons all route through the existing `closeModal()` JS in [main.js](../src/aifeeder/static/js/main.js). Added a check: if the modal's backdrop carries `data-modal-needs-reload`, `closeModal()` triggers `window.location.reload()` after clearing the slot. Both `ingest_panel.html` and `ingest_done.html` set this attribute. Means: whatever way the user dismisses the modal (deliberate Close or accidental Esc), the sidebar + feed update to reflect the new source. Alternative would have been HX-Refresh on every dismiss path — more route plumbing for the same outcome.
- **`POST /sources/{id}/ingest` is sync `def`, not `async def`.** `process_source` is blocking (yt-dlp + OpenAI calls — 30–60s for 10-item YouTube batches). FastAPI runs sync routes in a thread pool, so the event loop stays unblocked without us needing `asyncio.to_thread`. Simpler than the async-wrapped alternative. All other routes in the file are async — this is the only sync one and the docstring calls it out.
- **`process_source` reused from [refresh.py](../src/aifeeder/refresh.py) — not duplicated.** It already does fetch-dispatch + dedup-insert + summarize + per-item-commit + source-health updates, with `verbose=False` for non-CLI use. Web layer imports it directly; opens its own `connect()` connection, passes the source dict, gets back a `SourceResult`. Means the ingest panel inherits all the same failure semantics (`fetch_error` field, content-class skips, transient retries) — no behavior drift between CLI and web ingest.
- **`count` bounds clamped server-side to [1, 100]** (mirrors the HTML `min`/`max` input attrs). HTML5 client-side validation isn't enough — never trust the client. Clamp via `max(1, min(count, 100))` rather than 400-erroring on out-of-range, since the input has clear bounds and the user's intent ("ingest a lot" or "ingest one") is preservable.
- **Caveat that surfaced in smoke test (not changed):** for RSS, `process_source` dedup-inserts the *whole feed* (feedparser returns all available entries) and then summarizes only the first `per_source`. A "count=3" RSS ingest inserts ~20 items into `items` table but only summarizes 3; the remaining 17 sit as `pending` and would get summarized on the next `aifeeder refresh`. Existing behavior, not a regression — but it means "I picked 3" produces 3 feed-visible items + 17 latent pending items. Documented in state.md gotchas; would be a follow-on to cap `insert_new_items` if it becomes confusing.

**User response:** pending (just shipped; will surface in browser-check round).

**Refs:** decisions.md → *2026-05-22 — Source-add ingest flow: single-shot upfront count* (parent A-decision); ideas.md → *2026-05-22 Batched-continue ingest flow with running cost display* (deferred alternative); conversation → [2026-05-20_b670_ux-design.md](conversation/2026-05-20_b670_ux-design.md) (2026-05-22 ingest-flow turn).

---

_Last updated: 2026-05-22 — Source-add ingest panel shipped. Add → ingest panel (count input + spinner) → done panel (cost + close) → reload. process_source reused from refresh.py via sync def + FastAPI thread pool._

---

## 2026-05-22 — Source delete (red button on the source-edit modal)

User asked for a "delete source" affordance: red button with a delete icon on the bottom-left of the source-edit modal. Built end-to-end.

Engineering choices:

- **Hard delete with explicit cascade in app code.** Schema has no `ON DELETE CASCADE` (FKs are enforced but not cascading per [schema.sql](../schema.sql)); `delete_source()` in [web/writes.py](../src/aifeeder/web/writes.py) deletes bottom-up: feedback → cost_log → summaries → items → sources, all inside `BEGIN`/`COMMIT` (manual transaction so all five succeed or none do). Alternative was soft-delete via a `deleted_at` column — would enable undo + preserve cost_log history, but adds a column + WHERE clause to every read path. For v1 single-user local, hard-delete is the simpler call. If "I deleted by accident" surfaces in real use, soft-delete becomes a v1.x refactor.
- **HTMX `hx-confirm` for the destructive guard.** Browser-native `confirm()` dialog with the source name + "this cannot be undone" — cheapest mindful safeguard. Alternative was a two-step in-modal "are you sure?" panel; deferred unless the native prompt feels too jarring. The dialog text includes the source name so it can't be mindlessly accepted on the wrong source.
- **`DELETE /sources/{id}` route returns 204 + `HX-Refresh: true`.** Matches the existing source-save pattern. Reload is the cleanest way to reflect the source's disappearance from the sidebar + any feed items that vanish.
- **404 on missing source.** `writes.delete_source()` returns `False` when no row matched; the route raises HTTPException(404). Defensive — guards against double-click race conditions where two delete requests arrive in flight.
- **Delete button rendered only in edit mode** (`{% if not is_add %}` in [partials/source_modal.html](../src/aifeeder/templates/partials/source_modal.html)). The add modal has no source to delete yet.
- **Layout via `margin-right: auto` on the delete button**, not changing `.modal-actions` `justify-content`. This pushes delete to the left edge while cancel + save stay flush-right. Works without restructuring the action row; in add mode (no delete button) the cancel/save buttons stay correctly right-aligned. Used a soft red palette (`#B53A3A` border/text, `#F8E6E6` hover bg) tuned to the warm cream card aesthetic rather than a saturated `#FF0000`.
- **New `trash()` macro in [_icons.html](../src/aifeeder/templates/_icons.html)** — single-path SVG (rectangle bin + lid + 2 vertical lines), `fill: currentColor` so the button color inherits.

Smoke-tested end-to-end on running server: created a throwaway source (id 106) via POST /sources → confirmed delete button + hx-confirm + hx-delete attrs rendered in `/sources/106/edit` → `DELETE /sources/106` returned 204 + HX-Refresh:true → DB row gone (COUNT=0) → DELETE on nonexistent id returned 404. Then a cascade test: inserted source + 2 items + 1 summary + 1 cost_log + 1 feedback row via SQL → counts before delete: 1/2/1/1/1 → DELETE → counts after delete: 0/0/0/0/0. Cascade order works.

**User response:** pending (will surface in browser-check).

**Refs:** conversation → [2026-05-20_b670_ux-design.md](conversation/2026-05-20_b670_ux-design.md) (2026-05-22 delete-source turn); state.md → *Current focus* + *Out (schema ready, UI deferred)* (source-delete UI now removed from the "out" list).

---

_Last updated: 2026-05-22 — Source delete shipped. Red button bottom-left of edit modal, hx-confirm guard, hard-delete with explicit 5-step cascade in transaction, 204 + HX-Refresh on success. Verified cascade clears items / summaries / cost_log / feedback._
