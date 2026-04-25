from loguru import logger
from pwdlib import PasswordHash
from sqlmodel import Session

from ..commands import UserCommands
from ..models import User
from ..queries import UserQueries

pwd_context = PasswordHash.recommended()

class RegisterUserUseCase:
    def __init__(self, session: Session):
        self.queries = UserQueries(session)
        self.commands = UserCommands(session)

    def execute(self, email: str, raw_password: str, full_name: str | None) -> User:
        logger.info(f"Attempting to register new user: {email}")

        if self.queries.email_exists(email):
            logger.warning(f"Registration failed: Email {email} is already in use.")
            raise ValueError("Email already registered")

        logger.debug(f"Hashing password for {email}...")
        hashed_pwd = pwd_context.hash(raw_password)
        
        new_user = User(
            email=email, 
            hashed_password=hashed_pwd, 
            full_name=full_name
        )
        
        created_user = self.commands.create(new_user)
        
        logger.success(f"User {email} successfully registered with ID {created_user.id}")
        
        return created_user