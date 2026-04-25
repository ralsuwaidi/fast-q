# src/features/identity/use_cases/register_user.py
from sqlmodel import Session
from passlib.context import CryptContext
from ..models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class RegisterUserUseCase:
    def __init__(self, session: Session):
        self.session = session

    def execute(self, email: str, raw_password: str, full_name: str) -> User:
        # 1. Hash the password
        hashed_pwd = pwd_context.hash(raw_password)
        
        # 2. Create the SQLModel record
        user = User(
            email=email, 
            hashed_password=hashed_pwd, 
            full_name=full_name
        )
        
        # 3. Save to database
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        
        return user