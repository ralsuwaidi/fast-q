import enum
from datetime import date, datetime, timezone

from sqlmodel import Field, SQLModel


class SlotStatus(str, enum.Enum):
    to_contact = "To Contact"
    emailed = "Emailed"
    confirmed = "Confirmed"

class BookedSlot(SQLModel, table=True):
    """
    The resident's personal tracked shift.
    """
    id: int | None = Field(default=None, primary_key=True)
    
    # Links to the specific resident
    user_id: int = Field(foreign_key="user.id", index=True)
    
    # Copied from master slot
    hospital_name: str
    date: date
    specialty: str | None = Field(default=None) 
    physician: str
    time_block: str 
    contact_email: str
    
    # Workflow Tracking 
    status: SlotStatus = Field(default=SlotStatus.to_contact)
    notes: str | None = Field(default=None)
    
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )