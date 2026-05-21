"""Page + HTMX endpoints. Imported for its side effects (route registration).

Page routes return full HTML via Jinja2; HTMX endpoints return partials.
Notes + favourites + highlights use in-memory fakes; feedback callouts are
stateless echoes for v1 (real schema lands with `refresh`).
"""
import html
import json
import re
import sqlite3

from fastapi import HTTPException, Request, Form
from fastapi.responses import HTMLResponse, Response

from . import fakes, repo, writes
from .app import app, templates


# ---- accent palette mapping: 9 content_type_tags → 3 palette families ----
# warm = orange/sienna; cool = teal/slate; neutral = umber/cream
_TAG_TO_PALETTE: dict[str, str] = {
    "tutorial": "cool",
    "essay": "warm",
    "research paper": "cool",
    "news": "neutral",
    "link blog": "neutral",
    "interview": "warm",
    "review": "warm",
    "thread": "cool",
    "other": "neutral",
}


def _palette_for(tag: str | None) -> str:
    return _TAG_TO_PALETTE.get(tag or "other", "neutral")


def _shape_for(tag: str | None) -> str:
    """Card span shape: 'video' = 2col, 'text' = 2row, 'square' = 1x1."""
    if tag == "interview":  # treat as video-like in v1 if/when YouTube ships
        return "video"
    if tag in ("research paper", "essay"):
        return "text"
    return "square"


# Splits a "maybe" reason on the first hinge word ("although"/"but"/"though"),
# preserving the hinge token in the caution half so the locked voice survives.
# "yes" reasons have no hinge → caution stays None.
_REASON_HINGE_RE = re.compile(r"\s+(although|but|though)\s+", re.IGNORECASE)


def _split_reason(text: str | None) -> tuple[str | None, str | None]:
    if not text:
        return None, None
    m = _REASON_HINGE_RE.search(text)
    if not m:
        return text.strip(), None
    main = text[:m.start()].strip().rstrip(",")
    caution = text[m.start():].strip()
    return main, caution


def _enrich_item(item: dict) -> dict:
    """Add view-only fields: palette family, card shape, parsed key_points, fav flag."""
    item["palette"] = _palette_for(item.get("content_type_tag"))
    item["shape"] = _shape_for(item.get("content_type_tag"))
    raw_kp = item.get("key_points_json")
    item["key_points"] = json.loads(raw_kp) if raw_kp else []
    item["is_favourite"] = fakes.is_favourite(item["id"])
    item["reason_main"], item["reason_caution"] = _split_reason(item.get("relevance_reason"))
    return item


def _monogram(name: str) -> str:
    return (name or "?")[0].upper()


def _render_paragraphs_with_highlights(raw_content: str, highlights: list[str]) -> list[str]:
    """Split raw_content on blank lines, html-escape each paragraph, then wrap
    any stored highlight quote in <mark class="user-highlight">. First-match-only
    per quote per paragraph — naïve but fine for v1 (offset-tracking lands with
    real persistence)."""
    if not raw_content:
        return []
    paragraphs = [p.strip() for p in raw_content.split("\n\n") if p.strip()]
    rendered: list[str] = []
    for p in paragraphs:
        escaped = html.escape(p)
        for h in highlights:
            if not h:
                continue
            escaped_h = html.escape(h.strip())
            if not escaped_h:
                continue
            mark = f'<mark class="user-highlight">{escaped_h}</mark>'
            escaped = escaped.replace(escaped_h, mark, 1)
        rendered.append(escaped)
    return rendered


# ---------- pages ----------

@app.get("/", response_class=HTMLResponse)
async def loading(request: Request):
    sources = repo.list_sources()
    return templates.TemplateResponse(
        request,
        "loading.html",
        {"sources": sources},
    )


@app.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    user = repo.get_user()
    sources = repo.list_sources()
    items = [_enrich_item(i) for i in repo.list_feed_items()]
    for s in sources:
        s["monogram"] = _monogram(s["name"])
    return templates.TemplateResponse(
        request,
        "home.html",
        {
            "user": user,
            "sources": sources,
            "items": items,
            "sidebar_collapsed": False,
            "active_page": "home",
        },
    )


@app.get("/content/{item_id}", response_class=HTMLResponse)
async def content(request: Request, item_id: int):
    item = repo.get_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    item = _enrich_item(item)
    highlights = fakes.get_highlights(item_id)
    item["rendered_paragraphs"] = _render_paragraphs_with_highlights(
        item.get("raw_content") or "", highlights
    )
    user = repo.get_user()
    sources = repo.list_sources()
    for s in sources:
        s["monogram"] = _monogram(s["name"])
    notes = fakes.get_notes(item_id)
    return templates.TemplateResponse(
        request,
        "content.html",
        {
            "user": user,
            "sources": sources,
            "item": item,
            "notes": notes,
            "sidebar_collapsed": True,
            "active_page": "content",
        },
    )


# ---------- sidebar nav placeholders ----------

@app.get("/library", response_class=HTMLResponse)
async def library_page(request: Request):
    user = repo.get_user()
    sources = repo.list_sources()
    for s in sources:
        s["monogram"] = _monogram(s["name"])
    return templates.TemplateResponse(
        request,
        "list_page.html",
        {
            "user": user,
            "sources": sources,
            "page_title": "Library",
            "page_blurb": "Items you've read will land here. Coming with the next refresh wire.",
            "items": [],
            "sidebar_collapsed": False,
            "active_page": "library",
        },
    )


@app.get("/favourites", response_class=HTMLResponse)
async def favourites_page(request: Request):
    user = repo.get_user()
    sources = repo.list_sources()
    for s in sources:
        s["monogram"] = _monogram(s["name"])
    fav_ids = fakes.all_favourites()
    items = [_enrich_item(i) for i in repo.list_feed_items() if i["id"] in fav_ids]
    return templates.TemplateResponse(
        request,
        "list_page.html",
        {
            "user": user,
            "sources": sources,
            "page_title": "Favourites",
            "page_blurb": "Items you starred." if items else "No favourites yet. Star anything that's worth coming back to.",
            "items": items,
            "sidebar_collapsed": False,
            "active_page": "favourites",
        },
    )


@app.get("/notes", response_class=HTMLResponse)
async def notes_page(request: Request):
    user = repo.get_user()
    sources = repo.list_sources()
    for s in sources:
        s["monogram"] = _monogram(s["name"])
    pairs = fakes.all_notes()
    items_by_id = {i["id"]: _enrich_item(i) for i in repo.list_feed_items()}
    note_rows = [
        {"item": items_by_id.get(iid), "note": note}
        for iid, note in pairs
        if iid in items_by_id
    ]
    return templates.TemplateResponse(
        request,
        "notes_page.html",
        {
            "user": user,
            "sources": sources,
            "note_rows": note_rows,
            "sidebar_collapsed": False,
            "active_page": "notes",
        },
    )


# ---------- HTMX endpoints (return partials) ----------

@app.post("/feedback/{item_id}/refine", response_class=HTMLResponse)
async def feedback_refine(request: Request, item_id: int):
    return templates.TemplateResponse(
        request,
        "partials/feedback_thanks.html",
        {"item_id": item_id},
    )


@app.post("/feedback/{item_id}/{direction}", response_class=HTMLResponse)
async def feedback_callout(request: Request, item_id: int, direction: str):
    if direction not in ("up", "down"):
        raise HTTPException(status_code=400, detail="direction must be up or down")
    item = repo.get_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return templates.TemplateResponse(
        request,
        "partials/feedback_callout.html",
        {
            "item_id": item_id,
            "direction": direction,
            "source_why": item["source_why"],
            "relevance_reason": item["relevance_reason"],
        },
    )


@app.get("/notes/{item_id}/panel", response_class=HTMLResponse)
async def note_panel(request: Request, item_id: int, quote: str = ""):
    item = repo.get_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return templates.TemplateResponse(
        request,
        "partials/note_panel.html",
        {
            "item_id": item_id,
            "notes": fakes.get_notes(item_id),
            "quote": quote.strip(),
        },
    )


@app.post("/notes/{item_id}", response_class=HTMLResponse)
async def save_note(
    request: Request,
    item_id: int,
    title: str = Form(""),
    body: str = Form(""),
    quote: str = Form(""),
):
    quote_clean = quote.strip()
    fakes.add_note(
        item_id,
        title=title or "Untitled",
        body=body,
        quote=quote_clean or None,
    )
    if quote_clean:
        # Reload so the new highlight renders in the reader.
        return Response(status_code=204, headers={"HX-Refresh": "true"})
    return templates.TemplateResponse(
        request,
        "partials/note_panel.html",
        {
            "item_id": item_id,
            "notes": fakes.get_notes(item_id),
            "quote": "",
        },
    )


@app.post("/favourite/{item_id}", response_class=HTMLResponse)
async def favourite_toggle(request: Request, item_id: int):
    state = fakes.toggle_favourite(item_id)
    return templates.TemplateResponse(
        request,
        "partials/star_button.html",
        {"item_id": item_id, "is_favourite": state},
    )


# ---------- source edit (real DB write) ----------

@app.get("/sources/{source_id}/edit", response_class=HTMLResponse)
async def source_edit_modal(request: Request, source_id: int):
    source = repo.get_source(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    return templates.TemplateResponse(
        request,
        "partials/source_modal.html",
        {"source": source},
    )


@app.post("/sources/{source_id}", response_class=HTMLResponse)
async def source_save(
    request: Request,
    source_id: int,
    url: str = Form(""),
    why: str = Form(""),
):
    source = repo.get_source(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    try:
        writes.update_source(source_id, url=url, why=why)
    except sqlite3.IntegrityError:
        # sources.url is UNIQUE — re-render the modal with the user's edits + an error.
        return templates.TemplateResponse(
            request,
            "partials/source_modal.html",
            {
                "source": {**source, "url": url, "why": why},
                "error": "That URL is already used by another source. Pick a different one.",
            },
        )
    # Page reload so the updated url + why surface everywhere (sidebar hover-title, etc.)
    return Response(status_code=204, headers={"HX-Refresh": "true"})
