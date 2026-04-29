from dataclasses import dataclass
from sqlmodel import Session

from features.users.models import User

@dataclass
class DeleteUserCommand:
    user: User

class DeleteUserHandler:
    def __init__(self, db: Session):
        self.db = db

    def execute(self, command: DeleteUserCommand) -> None:
        """Removes a user from the database."""
        self.db.delete(command.user)
        self.db.commit()
