# src/features/residents/commands/delete_slot.py
from dataclasses import dataclass

from fastapi import HTTPException
from sqlmodel import Session

from ..models import BookedSlot


@dataclass
class DeleteSlotCommand:
    slot_id: int
    user_id: int

class DeleteSlotHandler:
    def __init__(self, db: Session):
        self.db = db

    def execute(self, command: DeleteSlotCommand) -> None:
        """Deletes a slot if it belongs to the requesting user."""
        
        slot = self.db.get(BookedSlot, command.slot_id)
        
        if not slot:
            raise HTTPException(status_code=404, detail="Slot not found")
            
        if slot.user_id != command.user_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this slot")
            
        self.db.delete(slot)
        self.db.commit()