import enum
from datetime import datetime, timezone

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class UserRole(str, enum.Enum):
    admin = "admin"
    resident = "resident"

class User(SQLModel, table=True):
    """
    The core User database model.
    """
    id: int | None = Field(default=None, primary_key=True)
    email: EmailStr = Field(unique=True, index=True)
    hashed_password: str
    full_name: str | None = Field(default=None)
    
    role: UserRole = Field(default=UserRole.resident)
    
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )