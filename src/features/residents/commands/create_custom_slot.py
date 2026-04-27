# src/features/residents/commands/create_custom_slot.py
from dataclasses import dataclass
from datetime import date

from sqlmodel import Session

from ..models import BookedSlot, SlotStatus


@dataclass
class CreateCustomSlotCommand:
    user_id: int
    hospital_name: str
    physician: str
    time_block: str
    contact_email: str
    date: date
    specialty: str | None = None
    status: SlotStatus = SlotStatus.to_contact
    notes: str | None = None

class CreateCustomSlotHandler:
    def __init__(self, db: Session):
        self.db = db

    def execute(self, command: CreateCustomSlotCommand) -> BookedSlot:
        """Executes the command to create a custom calendar slot."""
        
        slot = BookedSlot(
            user_id=command.user_id,
            hospital_name=command.hospital_name,
            physician=command.physician,
            time_block=command.time_block,
            contact_email=command.contact_email,
            date=command.date,
            specialty=command.specialty,
            status=command.status,
            notes=command.notes
        )
        
        self.db.add(slot)
        self.db.commit()
        self.db.refresh(slot)
        
        return slot