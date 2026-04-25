from sqlmodel import Session
from .models import User

class UserCommands:
    """Encapsulates all database write operations for the Users slice."""
    
    def __init__(self, session: Session):
        self.session = session

    def create(self, user: User) -> User:
        """Saves a new user to the database."""
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def update_status(self, user: User, is_active: bool) -> User:
        """Updates the active status of an existing user."""
        user.is_active = is_active
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def delete(self, user: User) -> None:
        """Removes a user from the database."""
        self.session.delete(user)
        self.session.commit()