# src/features/residents/commands/update_slot.py
from dataclasses import dataclass
from datetime import date
from typing import Optional

from fastapi import HTTPException
from sqlmodel import Session

from ..models import BookedSlot, SlotStatus


@dataclass
class UpdateSlotCommand:
    slot_id: int
    user_id: int
    hospital_name: str
    physician: str
    time_block: str
    contact_email: str
    date: date
    specialty: Optional[str] = None
    status: SlotStatus = SlotStatus.to_contact
    notes: Optional[str] = None


class UpdateSlotHandler:
    def __init__(self, db: Session):
        self.db = db

    def execute(self, command: UpdateSlotCommand) -> BookedSlot:
        slot = self.db.get(BookedSlot, command.slot_id)
        
        if not slot or slot.user_id != command.user_id:
            raise HTTPException(status_code=404, detail="Slot not found or unauthorized")

        slot.hospital_name = command.hospital_name
        slot.physician = command.physician
        slot.time_block = command.time_block
        slot.contact_email = command.contact_email
        slot.date = command.date
        slot.specialty = command.specialty
        slot.status = command.status
        slot.notes = command.notes

        self.db.add(slot)
        self.db.commit()
        self.db.refresh(slot)
        return slot
