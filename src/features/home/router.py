from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from core.auth import get_current_user
from core.database import get_session
from features.hospitals.models import Hospital
from features.users.models import User

router = APIRouter()
# Point Jinja exactly to this feature's template folder
templates = Jinja2Templates(directory=[
    "src/features/home/templates", 
    "src/templates"                 
])

@router.get("/", response_class=RedirectResponse)
async def home_redirect():
    """Redirects the root to the dashboard."""
    return RedirectResponse(url="/dashboard", status_code=302)

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(
    request: Request, 
    db: Session = Depends(get_session),
    current_user: User | None = Depends(get_current_user)
):
    """Renders the dashboard with hospital cards."""
    hospitals = db.exec(select(Hospital)).all()
    
    template_name = "partials/dashboard_content.html" if request.headers.get("hx-request") else "dashboard.html"
    
    return templates.TemplateResponse(
        request=request, 
        name=template_name,
        context={
            "hospitals": hospitals,
            "current_user": current_user
        }
    )

