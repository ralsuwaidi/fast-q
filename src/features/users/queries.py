from sqlmodel import Session, select

from .models import User


class UserQueries:
    """Encapsulates all database interactions for the Users slice."""
    
    def __init__(self, session: Session):
        self.session = session

    def email_exists(self, email: str) -> bool:
        """Checks if a user with this email already exists."""
        statement = select(User.id).where(User.email == email)
        result = self.session.exec(statement).first()
        return result is not None

    def get_by_email(self, email: str) -> User | None:
        """Fetches a full user model by email."""
        statement = select(User).where(User.email == email)
        return self.session.exec(statement).first()

    def get_active_users(self) -> list[User]:
        """Returns a list of all active users."""
        statement = select(User).where(User.is_active == True)
        return self.session.exec(statement).all()