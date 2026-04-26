from fastapi import APIRouter, Depends, Form, Request, Response
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from pwdlib import PasswordHash
from sqlmodel import Session

from core.database import get_session

from .commands import UserCommands
from .models import User
from .queries import UserQueries

router = APIRouter()

templates = Jinja2Templates(directory=[
    "src/features/users/templates",
    "src/templates"
])

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
    db: Session = Depends(get_session)
):
    """Handles the HTMX form submission for logging in."""
    queries = UserQueries(db)
    
    # 1. Fetch user using your existing class method
    user = queries.get_by_email(email)
    
    # 2. Verify user exists AND password hash matches
    if not user or not pwd_context.verify(password, user.hashed_password):
        # Return the error snippet styled to match your existing design
        return HTMLResponse(
            content="""
            <div class="p-3 bg-red-50 text-red-700 border border-red-200 rounded-lg text-sm text-center">
                Invalid email or password.
            </div>
            """, 
            status_code=400
        )
    
    # 3. Success! Set the HTTP-only cookie
    response.set_cookie(key="user_session", value=str(user.id), httponly=True)
    
    # 4. Trigger HTMX to redirect to the main schedule
    res = Response(
        status_code=200,
        headers={"HX-Redirect": "/mgh"},
    )
    res.set_cookie(key="user_session", value=str(user.id), httponly=True)

    return res

