from pydantic import BaseModel
from sqlmodel import Session

from features.users.models import MasterSlot


# We use a Pydantic schema to validate the incoming data before it hits the DB
class MasterSlotCreate(BaseModel):
    hospital_id: int
    day_of_week: str
    specialty: str | None = None
    physician: str
    time_block: str
    contact_email: str

def create_master_slot(db: Session, slot_data: MasterSlotCreate) -> MasterSlot:
    """
    COMMAND: Creates a new shift on the master schedule.
    """
    new_slot = MasterSlot(**slot_data.model_dump())
    db.add(new_slot)
    db.commit()
    db.refresh(new_slot)
    
    return new_slot