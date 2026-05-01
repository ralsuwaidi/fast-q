from fastapi import APIRouter, Depends, Form, Request, Response
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from pwdlib import PasswordHash
from sqlmodel import Session

from core.database import get_session

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
            <div class="p-3 bg-red-50 text-red-700 border border-red-200 rounded-lg text-sm text-center">
                Invalid email or password.
            </div>
            """,
            status_code=400,
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
# LOGOUT
# ==========================================
@router.post("/logout", response_class=HTMLResponse)
async def process_logout():
    """Handles logging out by clearing the session cookie."""
    res = Response(
        status_code=200,
        headers={"HX-Redirect": "/login"},
    )
    res.delete_cookie(key="user_session")
    return res
