from fastapi import Depends, Request
from sqlmodel import Session

from core.database import get_session
from features.users.models import User


def get_current_user(request: Request, db: Session = Depends(get_session)) -> User | None:
    """
    Checks the request cookies for a session. 
    Returns the User object if logged in, or None if logged out.
    """
    user_id = request.cookies.get("user_session")
    
    if not user_id:
        return None
        
    # Fetch the user by their ID
    return db.get(User, int(user_id))