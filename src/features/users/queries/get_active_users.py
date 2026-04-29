from dataclasses import dataclass
from sqlmodel import Session, select

from features.users.models import User

@dataclass
class GetActiveUsersQuery:
    pass

class GetActiveUsersHandler:
    def __init__(self, db: Session):
        self.db = db

    def execute(self, query: GetActiveUsersQuery) -> list[User]:
        """Returns a list of all active users."""
        statement = select(User).where(User.is_active == True)
        return self.db.exec(statement).all()
