# src/features/residents/queries/get_slot_details.py
from dataclasses import dataclass

from fastapi import HTTPException
from sqlmodel import Session

from ..models import BookedSlot


@dataclass
class GetSlotDetailsQuery:
    slot_id: int
    user_id: int

class GetSlotDetailsHandler:
    def __init__(self, db: Session):
        self.db = db

    def execute(self, query: GetSlotDetailsQuery) -> BookedSlot:
        """Fetches a specific slot, ensuring it belongs to the user."""
        slot = self.db.get(BookedSlot, query.slot_id)
        
        if not slot or slot.user_id != query.user_id:
            raise HTTPException(status_code=404, detail="Slot not found")
            
        return slot