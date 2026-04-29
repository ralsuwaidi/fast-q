from dataclasses import dataclass
from sqlmodel import Session, select

from features.users.models import User

@dataclass
class GetUserByEmailQuery:
    email: str

class GetUserByEmailHandler:
    def __init__(self, db: Session):
        self.db = db

    def execute(self, query: GetUserByEmailQuery) -> User | None:
        """Fetches a full user model by email."""
        statement = select(User).where(User.email == query.email)
        return self.db.exec(statement).first()
