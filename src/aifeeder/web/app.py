"""FastAPI app for AIFeeder. Single-user local web UI.

Loading → home → content. Sidebar partial on home + content.
"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ..db import apply_schema

_PKG_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = _PKG_DIR / "templates"
STATIC_DIR = _PKG_DIR / "static"

templates = Jinja2Templates(directory=str(TEMPLATE_DIR))


@asynccontextmanager
async def lifespan(app: FastAPI):
    apply_schema()
    yield


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

from . import routes  # noqa: E402,F401  -- registers routes on `app`
