from fastapi import APIRouter, Depends, Form, Request, Response
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from pwdlib import PasswordHash
from sqlmodel import Session

from core.database import get_session

from .commands.register_user import RegisterUserCommand, RegisterUserHandler
from .queries.get_user_by_email import GetUserByEmailHandler, GetUserByEmailQuery

router = APIRouter()

templates = Jinja2Templates(directory=["src/features/users/templates", "src/templates"])

pwd_context = PasswordHash.recommended()


# ==========================================
# LOGIN
# ==========================================
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Serves the login page UI."""
    return templates.TemplateResponse(request=request, name="login.html")


@router.post("/login", response_class=HTMLResponse)
async def process_login(
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_session),
):
    """Handles the HTMX form submission for logging in."""
    # 1. Fetch user
    user = GetUserByEmailHandler(db).execute(GetUserByEmailQuery(email))

    # 2. Verify user exists AND password hash matches
    if not user or not pwd_context.verify(password, user.hashed_password):
        # Return the error snippet styled to match your existing design
        return HTMLResponse(
            content="""
            <div class="animate-shake flex items-center gap-3 p-4 mb-4 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 border border-red-200 dark:border-red-800/30 rounded-2xl text-sm font-medium shadow-sm">
                <svg class="size-5 shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z" />
                </svg>
                <span>Invalid email or password. Please try again.</span>
            </div>
            """,
            status_code=200,
        )

    # 3. Success! Set the HTTP-only cookie
    response.set_cookie(key="user_session", value=str(user.id), httponly=True)

    # 4. Trigger HTMX to redirect to the main schedule
    res = Response(
        status_code=200,
        headers={"HX-Redirect": "/"},
    )
    res.set_cookie(key="user_session", value=str(user.id), httponly=True)

    return res


# ==========================================
# REGISTER
# ==========================================
@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Serves the registration page UI."""
    return templates.TemplateResponse(request=request, name="register.html")


@router.post("/register", response_class=HTMLResponse)
async def process_register(
    full_name: str = Form(""),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_session),
):
    """Handles the HTMX form submission for new account creation."""
    if len(password) < 8:
        return HTMLResponse(
            content='<div class="animate-shake">Password must be at least 8 characters.</div>',
            status_code=200,
        )

    try:
        user = RegisterUserHandler(db).execute(
            RegisterUserCommand(
                email=email.strip().lower(),
                raw_password=password,
                full_name=full_name.strip() or None,
            )
        )
    except ValueError as exc:
        return HTMLResponse(
            content=f'<div class="animate-shake">{exc}</div>',
            status_code=200,
        )

    res = Response(status_code=200, headers={"HX-Redirect": "/"})
    res.set_cookie(key="user_session", value=str(user.id), httponly=True)
    return res


# ==========================================
# LOGOUT
# ==========================================
@router.post("/logout", response_class=HTMLResponse)
async def process_logout():
    """Handles logging out by clearing the session cookie."""
    res = Response(
        status_code=200,
        headers={"HX-Redirect": "/"},
    )
    res.delete_cookie(key="user_session")
    return res
