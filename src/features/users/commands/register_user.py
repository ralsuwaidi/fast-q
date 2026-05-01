from dataclasses import dataclass, field
from loguru import logger
from pwdlib import PasswordHash
from sqlmodel import Session, select

from features.users.models import User, UserRole

pwd_context = PasswordHash.recommended()

@dataclass
class RegisterUserCommand:
    email: str
    raw_password: str
    full_name: str | None = None
    role: UserRole = field(default=UserRole.resident)

class RegisterUserHandler:
    def __init__(self, db: Session):
        self.db = db

    def execute(self, command: RegisterUserCommand) -> User:
        logger.info(f"Attempting to register new user: {command.email}")

        # Check if email exists
        statement = select(User.id).where(User.email == command.email)
        if self.db.exec(statement).first():
            logger.warning(f"Registration failed: Email {command.email} is already in use.")
            raise ValueError("Email already registered")

        logger.debug(f"Hashing password for {command.email}...")
        hashed_pwd = pwd_context.hash(command.raw_password)
        
        new_user = User(
            email=command.email, 
            hashed_password=hashed_pwd, 
            full_name=command.full_name,
            role=command.role,
        )
        
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        
        logger.success(f"User {command.email} (role={command.role}) successfully registered with ID {new_user.id}")
        return new_user
