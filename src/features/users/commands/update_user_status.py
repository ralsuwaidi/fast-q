from dataclasses import dataclass
from sqlmodel import Session

from features.users.models import User

@dataclass
class UpdateUserStatusCommand:
    user: User
    is_active: bool

class UpdateUserStatusHandler:
    def __init__(self, db: Session):
        self.db = db

    def execute(self, command: UpdateUserStatusCommand) -> User:
        """Updates the active status of an existing user."""
        command.user.is_active = command.is_active
        self.db.add(command.user)
        self.db.commit()
        self.db.refresh(command.user)
        return command.user
