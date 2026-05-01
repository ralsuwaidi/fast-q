from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from core.auth import get_current_user
from core.database import get_session
from features.hospitals.models import Hospital
from features.users.models import User
from features.users.queries.get_active_users import GetActiveUsersHandler, GetActiveUsersQuery

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

from features.hospitals.queries.get_all_hospitals import GetAllHospitalsQuery, GetAllHospitalsHandler

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(
    request: Request, 
    db: Session = Depends(get_session),
    current_user: User | None = Depends(get_current_user)
):
    """Renders the dashboard with hospital cards."""
    hospitals = GetAllHospitalsHandler(db).execute(GetAllHospitalsQuery())
    residents = db.exec(select(User)).all()
    
    template_name = "partials/dashboard_content.html" if request.headers.get("hx-request") else "dashboard.html"
    
    response = templates.TemplateResponse(
        request=request, 
        name=template_name,
        context={
            "hospitals": hospitals,
            "residents_count": len(residents),
            "current_user": current_user
        }
    )
    response.headers["HX-Trigger"] = "hospitalSelected"
    return response


# ==========================================
# ADMIN: PLATFORM USERS
# ==========================================
@router.get("/admin/users", response_class=HTMLResponse)
async def admin_users_page(
    request: Request,
    db: Session = Depends(get_session),
    current_user: User | None = Depends(get_current_user)
):
    """Renders the platform users management page (admin only)."""
    if not current_user or current_user.role != "admin":
        return RedirectResponse(url="/dashboard", status_code=302)

    all_users = GetActiveUsersHandler(db).execute(GetActiveUsersQuery())
    residents_count = sum(1 for u in all_users if u.role == "resident")
    admins_count = sum(1 for u in all_users if u.role == "admin")

    template_name = "partials/admin_users_content.html" if request.headers.get("hx-request") else "admin_users.html"

    return templates.TemplateResponse(
        request=request,
        name=template_name,
        context={
            "users": all_users,
            "residents_count": residents_count,
            "admins_count": admins_count,
            "current_user": current_user,
        }
    )
