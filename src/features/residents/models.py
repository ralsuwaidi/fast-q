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
    
    # Optional link to the public calendar. If it's None, it's a custom shift.
    master_slot_id: int | None = Field(default=None, foreign_key="masterslot.id")
    
    # Fallback fields for custom slots (when master_slot_id is None)
    custom_title: str | None = Field(default=None)
    custom_location: str | None = Field(default=None)
    date: date
    
    # Workflow Tracking 
    status: SlotStatus = Field(default=SlotStatus.to_contact)
    notes: str | None = Field(default=None)
    
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )