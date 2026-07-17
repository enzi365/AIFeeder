"""Page + HTMX endpoints. Imported for its side effects (route registration).

Page routes return full HTML via Jinja2; HTMX endpoints return partials.
Notes + favourites + highlights use in-memory fakes; feedback callouts are
stateless echoes for v1 (real schema lands with `refresh`).
"""
import html
import json
import re
import sqlite3
from contextlib import closing

from fastapi import HTTPException, Request, Form
from fastapi.responses import HTMLResponse, Response

from ..db import connect
from ..refresh import process_source
from . import fakes, repo, writes
from .app import app, templates

_I18N = {
    "en": {
        "app_label": "The app",
        "brand_line": "Mine the internet by your own intent",
        "eyebrow": "For the feed-fatigued",
        "hero_title": "Reclaim your attention.",
        "hero_copy": "Mine-fully turns endless feeds into deliberate choices, surfacing what you asked for instead of what algorithms push.",
        "demo_access": "Demo access",
        "login_title": "Step out of the scroll.",
        "login_copy": "Sign in to enter your quiet feed and decide what is worth your time today.",
        "email": "Email",
        "password": "Password",
        "login_button": "Reclaim my feed",
        "lang_label": "Language",
        "english": "English",
        "japanese": "日本語",
        "sky_title": "What's worth your time today, Emma?",
        "home_title": "Emma's Feed",
        "empty_feed": "No items yet. Run",
        "empty_feed_after": "to populate fixtures for UI development, or wire",
        "empty_feed_end": "for real data.",
        "home": "Home",
        "library": "Library",
        "favourites": "Favourites",
        "notes": "Notes",
        "sources": "Sources",
        "no_sources": "No sources yet.",
        "avatar_title": "Your reading persona",
        "thought_1": "curious about AI",
        "thought_2": "practitioner-led",
        "thought_3": "no fluff",
        "purpose": "Purpose",
        "key_points": "Key points",
        "back_to_feed": "back to feed",
        "from": "from",
        "open_original": "open original",
        "no_content": "No content body available.",
        "note_from_selection": "+ Note from selection",
        "worth_my_time": "Worth my time",
        "didnt_fit": "Didn't fit",
        "add_note": "Add a note",
        "circle_why_1": None,
        "circle_why_2": None,
    },
    "ja": {
        "app_label": "アプリ",
        "brand_line": "自分の意図で、インターネットを掘り出す",
        "eyebrow": "フィード疲れのあなたへ",
        "hero_title": "注意を取り戻そう。",
        "hero_copy": "Mine-fullyは、終わりのないフィードを意識的な選択へ変えます。アルゴリズム任せではなく、あなたが求めたものを届けます。",
        "demo_access": "デモアクセス",
        "login_title": "スクロールから抜け出そう。",
        "login_copy": "静かなフィードに入り、今日あなたの時間に値するものを選びましょう。",
        "email": "メール",
        "password": "パスワード",
        "login_button": "自分のフィードを取り戻す",
        "lang_label": "言語",
        "english": "English",
        "japanese": "日本語",
        "sky_title": "今日、あなたの時間に値するものは？ Emma",
        "home_title": "Emmaのフィード",
        "empty_feed": "まだ項目がありません。",
        "empty_feed_after": "でUI開発用のサンプルを追加するか、",
        "empty_feed_end": "で実データを取得してください。",
        "home": "ホーム",
        "library": "ライブラリ",
        "favourites": "お気に入り",
        "notes": "ノート",
        "sources": "ソース",
        "no_sources": "ソースはまだありません。",
        "avatar_title": "あなたの読書ペルソナ",
        "thought_1": "AIへの好奇心",
        "thought_2": "実践者目線",
        "thought_3": "余計な情報なし",
        "purpose": "目的",
        "key_points": "要点",
        "back_to_feed": "フィードに戻る",
        "from": "出典",
        "open_original": "元記事を開く",
        "no_content": "本文はありません。",
        "note_from_selection": "+ 選択部分からノート",
        "worth_my_time": "読む価値あり",
        "didnt_fit": "合わなかった",
        "add_note": "ノートを追加",
        "circle_why_1": "実践的なAIエンジニアリングを追う。新しいLLM、動くコード例、実際に作っている人の洞察を優先。",
        "circle_why_2": "機械学習とAIエージェントの新しい研究を把握する。数式中心より、作り手に役立つ応用・システム寄りの内容を優先。",
    },
}


def _lang(request: Request) -> str:
    return "ja" if request.query_params.get("lang") == "ja" else "en"


def _text(lang: str) -> dict[str, str]:
    return _I18N.get(lang, _I18N["en"])


def _lang_suffix(lang: str) -> str:
    return "?lang=ja" if lang == "ja" else ""


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


# Maps the structural source_type → a coarse "format" label used to pick a
# media-type icon on the home card. source_type is set at ingest time and
# can't drift like content_type_tag (which is AI-derived).
_SOURCE_TYPE_TO_FORMAT: dict[str, str] = {
    "youtube_channel": "video",
    "rss": "reading",
}


def _format_for(source_type: str | None) -> str:
    return _SOURCE_TYPE_TO_FORMAT.get(source_type or "", "reading")


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
    """Add view-only fields: palette family, card shape, parsed key_points, fav flag,
    format icon dispatch, and (for YT items) the bare video_id used by the iframe."""
    item["palette"] = _palette_for(item.get("content_type_tag"))
    item["shape"] = _shape_for(item.get("content_type_tag"))
    item["format"] = _format_for(item.get("source_type"))
    item["video_id"] = item.get("external_id") if item.get("source_type") == "youtube_channel" else None
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
async def landing(request: Request):
    lang = _lang(request)
    return templates.TemplateResponse(
        request,
        "landing.html",
        {"lang": lang, "t": _text(lang), "lang_suffix": _lang_suffix(lang)},
    )


@app.get("/sky", response_class=HTMLResponse)
async def loading(request: Request):
    lang = _lang(request)
    sources = repo.list_sources()
    return templates.TemplateResponse(
        request,
        "loading.html",
        {
            "sources": sources,
            "lang": lang,
            "t": _text(lang),
            "next_url": f"/home{_lang_suffix(lang)}",
        },
    )


@app.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    lang = _lang(request)
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
            "lang": lang,
            "t": _text(lang),
            "lang_suffix": _lang_suffix(lang),
        },
    )


@app.get("/content/{item_id}", response_class=HTMLResponse)
async def content(request: Request, item_id: int):
    lang = _lang(request)
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
            "lang": lang,
            "t": _text(lang),
            "lang_suffix": _lang_suffix(lang),
        },
    )


# ---------- sidebar nav placeholders ----------

@app.get("/library", response_class=HTMLResponse)
async def library_page(request: Request):
    lang = _lang(request)
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
            "lang": lang,
            "t": _text(lang),
            "lang_suffix": _lang_suffix(lang),
        },
    )


@app.get("/favourites", response_class=HTMLResponse)
async def favourites_page(request: Request):
    lang = _lang(request)
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
            "lang": lang,
            "t": _text(lang),
            "lang_suffix": _lang_suffix(lang),
        },
    )


@app.get("/notes", response_class=HTMLResponse)
async def notes_page(request: Request):
    lang = _lang(request)
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
            "lang": lang,
            "t": _text(lang),
            "lang_suffix": _lang_suffix(lang),
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


# ---------- source add (real DB write) ----------
# Registered BEFORE the source-edit routes so the literal `/sources/new`
# and `/sources` paths win over the `{source_id}` template matches.

@app.get("/sources/new", response_class=HTMLResponse)
async def source_add_modal(request: Request):
    return templates.TemplateResponse(
        request,
        "partials/source_modal.html",
        {"source": {"id": None, "name": "", "url": "", "why": ""}},
    )


@app.post("/sources", response_class=HTMLResponse)
async def source_create(
    request: Request,
    name: str = Form(""),
    url: str = Form(""),
    why: str = Form(""),
):
    name_clean, url_clean, why_clean = name.strip(), url.strip(), why.strip()
    if not (name_clean and url_clean and why_clean):
        return templates.TemplateResponse(
            request,
            "partials/source_modal.html",
            {
                "source": {"id": None, "name": name_clean, "url": url_clean, "why": why_clean},
                "error": "All fields are required.",
            },
        )
    try:
        new_id = writes.insert_source(name_clean, url_clean, why_clean)
    except sqlite3.IntegrityError:
        return templates.TemplateResponse(
            request,
            "partials/source_modal.html",
            {
                "source": {"id": None, "name": name_clean, "url": url_clean, "why": why_clean},
                "error": "That URL is already used by another source. Pick a different one.",
            },
        )
    # Hand off to the ingest panel rather than reloading immediately — the user
    # picks how many items to fetch + summarize for this new source. Closing
    # the panel triggers the reload (via data-modal-needs-reload on the backdrop).
    source = repo.get_source(new_id)
    return templates.TemplateResponse(
        request,
        "partials/ingest_panel.html",
        {"source": source},
    )


# ---------- source ingest (real DB write + AI calls) ----------
# Sync `def` so FastAPI runs it in a thread pool — `process_source` is blocking
# (yt-dlp fetches + OpenAI calls can take 30–60s for a 10-item YouTube batch),
# and we don't want to block the event loop.

@app.post("/sources/{source_id}/ingest", response_class=HTMLResponse)
def source_ingest(request: Request, source_id: int, count: int = Form(10)):
    source = repo.get_source(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    count = max(1, min(count, 100))  # mirror the input's min/max; never trust the client
    with closing(connect()) as conn:
        result = process_source(
            conn, source,
            per_source=count,
            verbose=False,
            dry_run=False,
        )
    return templates.TemplateResponse(
        request,
        "partials/ingest_done.html",
        {"source": source, "result": result},
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


@app.delete("/sources/{source_id}", response_class=HTMLResponse)
async def source_delete(request: Request, source_id: int):
    """Hard-delete a source + all its items/summaries/cost_log/feedback rows.
    UI guards with `hx-confirm` before the request even fires."""
    if writes.delete_source(source_id):
        return Response(status_code=204, headers={"HX-Refresh": "true"})
    raise HTTPException(status_code=404, detail="Source not found")


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
