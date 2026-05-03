from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from core.auth import get_current_user
from features.users.models import User

router = APIRouter()
templates = Jinja2Templates(directory=["src/features/info/templates", "src/templates"])


def _render(request: Request, page: str, current_user: User | None) -> HTMLResponse:
    is_htmx = request.headers.get("hx-request") == "true"
    name = f"partials/{page}_content.html" if is_htmx else f"{page}.html"
    response = templates.TemplateResponse(
        request=request,
        name=name,
        context={"current_user": current_user},
    )
    response.headers["HX-Trigger"] = "hospitalSelected"
    return response


@router.get("/info/key-information", response_class=HTMLResponse)
async def key_information_page(
    request: Request,
    current_user: User | None = Depends(get_current_user),
):
    return _render(request, "key_information", current_user)


@router.get("/info/contacts", response_class=HTMLResponse)
async def contacts_page(
    request: Request,
    current_user: User | None = Depends(get_current_user),
):
    return _render(request, "contacts", current_user)
