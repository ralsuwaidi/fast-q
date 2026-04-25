from datetime import datetime, timezone
from pydantic import EmailStr
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    """
    The core User database model.
    """
    # Use an integer ID for SQLite simplicity, but UUIDs are great for Postgres
    id: int | None = Field(default=None, primary_key=True)
    
    # We use Pydantic's EmailStr for automatic validation, and index=True for fast lookups
    email: EmailStr = Field(unique=True, index=True)
    
    # Never store raw passwords! This will store the bcrypt hash
    hashed_password: str
    
    full_name: str | None = Field(default=None)
    
    # Standard flags for user management
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    
    # Automatically set the timestamp when the user is created
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )