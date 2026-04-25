from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from core.database import get_session

router = APIRouter()
# Point Jinja exactly to this feature's template folder
templates = Jinja2Templates(directory="src/features/home/templates")


@router.get("/", response_class=HTMLResponse)
async def home_page(request: Request, db: Session = Depends(get_session)):
    """Renders the main layout."""
    return templates.TemplateResponse(request=request, name="index.html")


@router.post("/ping", response_class=HTMLResponse)
async def ping_server():
    """An HTMX endpoint returning a partial HTML snippet."""
    return "<b>Pong!</b> The database is ready and HTMX is working."
