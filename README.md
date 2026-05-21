# AIFeeder

Personal AI-powered RSS reader — mindful content consumption. Local-only, single-user.

## Quick start

```bash
pip install -e .
cp .env.example .env  # add your OPENAI_API_KEY
aifeeder init         # create the database, seed sources
aifeeder refresh      # fetch sources, summarize new items, persist
```

Then open the web UI (coming in the next build step).

## Design notes

See [`docs/`](docs/) for the strategic context:

- [`docs/state.md`](docs/state.md) — where the project is right now
- [`docs/decisions.md`](docs/decisions.md) — product / mission / scope decisions
- [`docs/engineering-decisions.md`](docs/engineering-decisions.md) — engineering choices
- [`docs/ideas.md`](docs/ideas.md) — deferred features
- [`docs/workflow-notes.md`](docs/workflow-notes.md) — how to work with Claude on this project
