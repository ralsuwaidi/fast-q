from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from core.auth import get_current_user
from core.database import get_session
from features.hospitals.models import Hospital
from features.users.models import User, UserRole
from features.users.queries.get_active_users import GetActiveUsersHandler, GetActiveUsersQuery
from features.users.commands.register_user import RegisterUserCommand, RegisterUserHandler

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


# ==========================================
# ADMIN: CREATE USER (GET — show form)
# ==========================================
@router.get("/admin/users/new", response_class=HTMLResponse)
async def create_user_page(
    request: Request,
    current_user: User | None = Depends(get_current_user),
):
    """Renders the create-user form (admin only)."""
    if not current_user or current_user.role != "admin":
        return RedirectResponse(url="/dashboard", status_code=302)

    template_name = "partials/create_user_content.html" if request.headers.get("hx-request") else "create_user.html"

    return templates.TemplateResponse(
        request=request,
        name=template_name,
        context={"current_user": current_user},
    )


# ==========================================
# ADMIN: CREATE USER (POST — process form)
# ==========================================
@router.post("/admin/users/new", response_class=HTMLResponse)
async def create_user(
    request: Request,
    db: Session = Depends(get_session),
    current_user: User | None = Depends(get_current_user),
    full_name: str = Form(default=""),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    role: str = Form(default="resident"),
):
    """Handles the create-user form submission (admin only)."""
    if not current_user or current_user.role != "admin":
        return RedirectResponse(url="/dashboard", status_code=302)

    template_name = "partials/create_user_content.html" if request.headers.get("hx-request") else "create_user.html"

    def error(msg: str):
        return templates.TemplateResponse(
            request=request,
            name=template_name,
            context={
                "current_user": current_user,
                "error_message": msg,
                "full_name": full_name,
                "email": email,
            },
        )

    if password != confirm_password:
        return error("Passwords do not match.")

    if len(password) < 8:
        return error("Password must be at least 8 characters.")

    user_role = UserRole.admin if role == "admin" else UserRole.resident

    try:
        RegisterUserHandler(db).execute(
            RegisterUserCommand(
                email=email,
                raw_password=password,
                full_name=full_name or None,
                role=user_role,
            )
        )
    except ValueError as exc:
        return error(str(exc))

    # Success → redirect back to the users list
    response = RedirectResponse(url="/admin/users", status_code=303)
    return response


# ==========================================
# ADMIN: DELETE USER
# ==========================================
@router.delete("/admin/users/{user_id}", response_class=HTMLResponse)
async def delete_user(
    user_id: str,
    request: Request,
    db: Session = Depends(get_session),
    current_user: User | None = Depends(get_current_user),
):
    """Deletes a user (admin only)."""
    if not current_user or current_user.role != "admin":
        return HTMLResponse("Unauthorized", status_code=403)

    if str(current_user.id) == user_id:
        return HTMLResponse("You cannot delete your own account.", status_code=400)

    user = db.get(User, user_id)
    if user:
        db.delete(user)
        db.commit()

    # Re-render the admin users page (as a partial if requested via HTMX)
    return await admin_users_page(request, db, current_user)
