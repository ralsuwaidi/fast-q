from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from pwdlib import PasswordHash
from .queries import UserQueries
from core.database import get_session
from .models import User

router = APIRouter()

# Tell Jinja to look in the local feature folder FIRST, then the global folder
templates = Jinja2Templates(directory=[
    "src/features/users/templates",
    "src/templates"
])

# Password hashing configuration
pwd_context = PasswordHash.recommended()


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Serves the registration page UI."""
    return templates.TemplateResponse(request=request, name="register.html")


@router.post("/register", response_class=HTMLResponse)
async def register_user(
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(None),
    db: Session = Depends(get_session)
):
    """Handles the HTMX form submission for creating a new user."""
    queries = UserQueries(db)
    
    # 1. Check if user already exists
    if queries.email_exists(email):
        # Return an HTML snippet with Tailwind styling for an error
        return """
        <div class="p-3 bg-red-50 text-red-700 border border-red-200 rounded-lg text-sm">
            That email is already registered. Please log in.
        </div>
        """

    # 2. Hash password and create the user record
    hashed_pwd = pwd_context.hash(password)
    new_user = User(
        email=email, 
        hashed_password=hashed_pwd, 
        full_name=full_name
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 3. Return a success message snippet
    # In a real app, you might also set an HTTP-only cookie here to log them in automatically
    display_name = new_user.full_name if new_user.full_name else new_user.email
    return f"""
    <div class="p-4 bg-green-50 text-green-700 border border-green-200 rounded-lg text-center">
        <h3 class="font-bold mb-1">Account Created!</h3>
        <p class="text-sm">Welcome to Fast-Q, {display_name}.</p>
    </div>
    """