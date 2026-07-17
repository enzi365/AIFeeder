# AIFeeder — Mindful Content Feed

A personal, local-first AI reader that filters RSS feeds and YouTube channels against a user-written *intent* (a "why" per source), so every new item arrives pre-judged as **worth reading**, **worth a shot with caveats**, or **skip** — without the unread counters, streaks, and algorithmic nudges that mainstream readers ship by default.

---

## Overview

### Problem

**Who is affected?**
A single user (the builder) who wants to follow a handful of high-signal RSS feeds and YouTube channels — without the doomscroll-by-default experience of mainstream readers: endless chronological lists, unread badges, engagement nudges, and algorithmic "up next" surfaces.

**What is the issue?**
Following good sources still produces a firehose of items the user doesn't actually want to read. Existing readers either show *everything chronologically* (no filtering, just volume) or *rank by opaque engagement signals* (optimized for time-on-app, not for intent). Neither matches the real goal: *"show me the items that match what I said I cared about, hide the rest, and don't manufacture urgency around any of it."*

### Outcome

A working, end-to-end prototype that:

- **Ingests** RSS/Atom feeds (`feedparser`) and YouTube channels (`yt-dlp` + `youtube-transcript-api`).
- **Summarizes** each new item with an LLM (GPT-4o-mini by default) *against the source's "why" string*, producing a structured verdict (`yes` / `maybe` / `no`), a one-line reason in a locked mindful tone ("Worth reading if…" / "Worth a shot for X although Y" / "Skip — this is mostly Z"), a purpose line, key points, and content/style tags.
- **Filters** the home feed to `yes` and `maybe` items only — `no` verdicts are stored (for dedup + cost accounting) but never reach the feed.
- **Renders** each item as a card with an apple verdict indicator (whole = yes, bitten = maybe), a colour-split reason/caveat block (sage = recommendation, sienna = caveat), and a format icon (video / audio / reading).
- **Reads** in a clean single-column view with the AI's pre-frame ("Purpose" + "Key points") above the content, an embedded `youtube-nocookie` iframe for video items, and in-text highlight → quote-attached notes.
- **Runs entirely local** — one SQLite file, no telemetry, no accounts, no remote services beyond the LLM API call.

**Measurable results (latest smoke run):**

| Metric | Value |
|---|---|
| Test suite | 43 tests, all green (~1.2s) |
| Sources supported | RSS/Atom + YouTube channels |
| Cost per RSS item | ~$0.0001 |
| Cost per YouTube transcript | ~$0.0015 |
| Ingest latency (10 RSS items) | ~10–15s |
| Ingest latency (10 YouTube videos) | ~30–60s |
| Page + HTMX routes | 7 pages + 11 endpoints (all 200 in smoke test) |

---

## Demo

The user flow from cold start to reading a filtered item, in seven steps:

**1. Start the app** — `aifeeder serve` → open `http://127.0.0.1:8000/home`.

![Home grid](assets/home-grid.png)

The home page shows a grid of cards: only items the AI flagged `yes` or `maybe`, each with a verdict indicator (whole apple = yes, bitten apple = maybe), a sage reason block + optional sienna caveat block, a format icon (video / audio / reading), and the content-type tag.

**2. Add a source** — click the orange `+` button in the sidebar.

![Add-source modal](assets/add-source-modal.png)

Fill in **Name**, **URL** (any RSS feed or YouTube channel URL — the type is auto-detected from the host), and **Why** — the intent the AI will use to evaluate every item from this source.

**3. Pick how many to ingest** — on save, the modal hands off to an ingest panel.

![Ingest panel](assets/ingest-panel.png)

Choose how many items to fetch + summarize *right now* (default 10, bounds [1, 100]). Click **Ingest** — a pulse animation runs during the fetch.

**4. See the result** — the done panel shows item counts + actual cost.

![Ingest done](assets/ingest-done.png)

Close the modal → the page reloads and the new items appear in the feed.

**5. Open an item** — click a card.

![Content page (RSS)](assets/content-page-rss.png)

The reader shows the title + source line, the AI's pre-frame block ("Purpose" + "Key points"), then the original content split into paragraphs. Highlight any phrase → a floating "Note from selection" button → write a note attached to the quoted passage (which stays highlighted on reload).

**6. Open a YouTube item** — same shape, with an embedded `youtube-nocookie` iframe below the AI pre-frame, then the transcript paragraphs.

![Content page (YouTube)](assets/content-page-youtube.png)

The iframe sits *below* the pre-frame on purpose — frame the watch decision before pressing play.

**7. Edit or delete a source** — click any source name in the sidebar.

![Source edit modal with delete](assets/delete-confirm.png)

The same modal opens in edit mode (URL + Why editable). A red **delete source** button (bottom-left) triggers a browser confirm dialog naming the source before issuing the destructive request, which cascades through all child tables in one transaction.

---

## Technology Stack

### Frontend components

Client-side technologies for user interaction:

- **HTML5 + [Jinja2](https://jinja.palletsprojects.com/) templates** — server-rendered HTML; no SPA framework. One base layout + per-page templates + reusable partials.
- **[HTMX](https://htmx.org/)** — declarative AJAX via `hx-get` / `hx-post` / `hx-delete` / `hx-target` / `hx-confirm` / `hx-indicator` attributes. Modal open, source CRUD, feedback callouts, notes, favourites, and the ingest panel all work without hand-written client request code.
- **Hand-written CSS** (no framework) — a custom palette (cream / warm-sienna / cool-teal / sage / muted-brown) as CSS variables; per-card colour dispatch, format-icon colours, and the sage/sienna reason-split all driven by class names.
- **Vanilla JavaScript** (one ~80-line file) — modal close handling (Esc / backdrop / X / Cancel), the `data-modal-needs-reload` multi-step-modal pattern, and the text-selection floating popup for in-text note-taking.
- **[Google Fonts](https://fonts.google.com/)** — Fraunces (serif; headings) + Source Sans 3 (sans; body).

### Backend components

Server-side technologies for processing, APIs, and coordination:

- **[Python 3.11+](https://www.python.org/)** — required minimum (developed/tested on 3.13).
- **[FastAPI](https://fastapi.tiangolo.com/)** — serves both full-page routes (Jinja-rendered HTML) and HTMX partial endpoints.
- **[Uvicorn](https://www.uvicorn.org/)** — ASGI server, launched via `aifeeder serve`.
- **[SQLite](https://www.sqlite.org/)** via the stdlib `sqlite3` module — single-file local DB, no ORM. Foreign keys enforced; the source-delete write uses a manual multi-step cascade in one transaction.
- **[OpenAI Python SDK](https://github.com/openai/openai-python)** — LLM calls (GPT-4o-mini default), structured tool-call output for the summary schema.
- **[Anthropic SDK](https://github.com/anthropics/anthropic-sdk-python)** — wired as an alternate provider (selectable via env), not the production default.
- **[feedparser](https://feedparser.readthedocs.io/)** — RSS/Atom ingestion.
- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** — YouTube channel enumeration (with the channel-root → `/videos` sub-playlist drill-through).
- **[youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)** — fetches auto-caption transcripts directly.
- **[python-dotenv](https://github.com/theskumar/python-dotenv)** — `.env` loading for API keys + model override.
- **[python-multipart](https://github.com/Kludex/python-multipart)** — HTMX form-post handling for FastAPI.
- **[httpx](https://www.python-httpx.org/)** — HTTP client (transitive, used by the OpenAI SDK).
- **[pytest](https://docs.pytest.org/)** — test runner (dev dependency).

---

## Installation

Requires **Python 3.11+** and an **OpenAI API key**.

```bash
# 1. Clone + enter the repo
git clone <repo-url> aifeeder
cd aifeeder

# 2. Create a virtualenv + install
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# 3. Add your API key
cp .env.example .env
# Edit .env and paste your OPENAI_API_KEY

# 4. Apply the schema + seed the two starter sources (Simon Willison, ArXiv cs.AI)
aifeeder init

# 5. (Optional) Pull the first few items right now
aifeeder refresh --per-source 5

# 6. Launch the web UI
aifeeder serve
# → http://127.0.0.1:8000/home
```

To install dev dependencies and run the tests:

```bash
pip install -e ".[dev]"
pytest
```

---

## Usage

### CLI

| Command | What it does |
|---|---|
| `aifeeder init` | Apply schema, seed sources + user row. Idempotent. |
| `aifeeder preview [--per-source N]` | Fetch + summarize + print to stdout. **No DB writes.** Handy for testing prompt changes (default 3/source). |
| `aifeeder refresh` | Fetch new items from all sources, summarize them, persist. Per-item commit, so a crash mid-run leaves clean state. Flags: `--per-source N` (default 10), `--source-id N` (single source), `--dry-run` (fetch/parse only — no AI, no writes), `--quiet`. |
| `aifeeder seed-fake` | Insert 12 fixture items spanning all content-type tags, for UI dev without spending tokens. Idempotent. |
| `aifeeder serve` | Start the local web UI. Flags: `--host` (default `127.0.0.1`), `--port` (default `8000`), `--no-reload`. |

### Web UI

After `aifeeder serve`:

1. Open `http://127.0.0.1:8000/home` — see the filtered feed.
2. Click a card → reader view with the AI pre-frame above the content.
3. Highlight text → "Note from selection" → write a quote-attached note.
4. Add a source with the sidebar `+` button; choose how many items to ingest now.
5. Click any source name in the sidebar to edit its URL/Why, or delete it.

### Expected behaviour

- New items are **deduplicated** by `(source_id, external_id)` — re-running `refresh` never re-summarizes a known item.
- YouTube videos **without an English auto-caption transcript** are skipped at ingest (no DB row, no wasted AI call).
- `no`-verdict items **are inserted** (for cost accounting + dedup) but **never appear** in the home feed.
- **Source deletion cascades** to feedback / cost_log / summaries / items in a single transaction (no `ON DELETE CASCADE` in the schema — it's done explicitly).

### Tests

```bash
pytest             # 43 tests, ~1.2s
pytest -v          # verbose
pytest tests/test_writes.py   # a single file
```

The suite covers the trickiest non-network logic: URL-based source-type detection, the (deliberately brittle) reason-splitter regex and its edge cases, the transcript pseudo-paragraph chunker with mock snippets, the exception → failure-class mapping that drives the retry policy, and the cascade-delete order against a real temp SQLite database.

---

## Project Structure

```
AIFeeder/
├── README.md                  # this file
├── LICENSE                    # MIT
├── .env.example               # template for API key + model override
├── pyproject.toml             # package metadata, deps, pytest config
├── schema.sql                 # SQLite schema (idempotent; seeds 2 starter sources)
├── CLAUDE.md                  # AI co-developer instructions (read every session)
│
├── src/aifeeder/              # application source
│   ├── cli.py                 # `aifeeder` entrypoint (init / preview / refresh / serve / seed-fake)
│   ├── db.py                  # SQLite connection + schema apply
│   ├── ingest.py              # RSS (feedparser) + YouTube (yt-dlp + transcript-api) fetch + chunk
│   ├── ai.py                  # LLM client + summarize() — OpenAI + Anthropic paths
│   ├── refresh.py             # orchestration: fetch → dedup → summarize-with-retry → per-item commit
│   ├── seed_fake.py           # fixture items for UI-only dev
│   ├── prompts/
│   │   └── summarize_v1.txt   # locked AI prompt with the three tone phrasings
│   ├── web/                   # FastAPI app
│   │   ├── app.py             # app + Jinja2 setup
│   │   ├── routes.py          # page + HTMX endpoints + pure view helpers (palette / format / split_reason)
│   │   ├── repo.py            # read-only DB queries (writes go through writes.py — by design)
│   │   ├── writes.py          # UI→DB writes (insert / update / delete_source)
│   │   └── fakes.py           # in-memory notes/favourites/highlights (wiped on reload)
│   ├── templates/             # Jinja2 templates
│   │   ├── base.html / home.html / content.html / loading.html / list_page.html / notes_page.html
│   │   ├── _sidebar.html / _card.html / _icons.html
│   │   └── partials/          # HTMX fragments (source_modal, ingest_panel, ingest_done, note_panel, …)
│   └── static/
│       ├── css/               # main.css, cards.css, content.css, circles.css
│       └── js/main.js         # ~80 lines — modal close, selection popup, feedback chips
│
├── tests/                     # pytest suite (43 tests, ~1.2s)
│   ├── conftest.py            # tmp_db fixture (per-test temp SQLite)
│   ├── test_writes.py         # source-type detection + cascade delete + insert
│   ├── test_routes_pure.py    # palette + format dispatch + reason splitter
│   ├── test_ingest.py         # transcript chunker (mock snippets)
│   └── test_refresh.py        # classify_exception → failure_class
│
├── docs/                      # extended docs + AI co-dev artefacts
│   ├── state.md               # where the project is right now (frequently updated)
│   ├── decisions.md           # A-category: product / mission / UX / AI-behaviour decisions
│   ├── engineering-decisions.md  # B-category: routine engineering choices
│   ├── ideas.md               # deferred ideas — the parking lot for v2+
│   ├── workflow-notes.md      # durable practices (the A/B/C decision split, etc.)
│   └── conversation/          # per-session intent-summaries (not transcripts)
│
├── assets/                    # screenshots referenced above
└── aifeeder.db                # local SQLite (gitignored)
```

**Key folders at a glance:**

- **`src/aifeeder/`** — the app. Ingestion (`ingest.py`), AI summarization (`ai.py`), the refresh orchestrator (`refresh.py`), and the CLI (`cli.py`) form the pipeline; `web/` is the FastAPI + HTMX UI on top of it.
- **`src/aifeeder/web/`** — read/write split: `repo.py` is read-only by convention, all persistence goes through `writes.py`, and `fakes.py` holds in-memory stand-ins (notes / favourites / highlights) pending a real schema migration.
- **`tests/`** — pytest suite targeting the non-network logic most likely to break silently.
- **`docs/`** — the decision trail. `decisions.md` / `engineering-decisions.md` are append-only records of *why* each choice was made; `state.md` is the live snapshot; `conversation/` traces intent over time.

---

## License

[MIT](LICENSE). Personal use, no warranty, modify freely.
