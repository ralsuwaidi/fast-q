from dataclasses import dataclass

from sqlmodel import Session

from ..models import BookedSlot, SlotStatus


from datetime import date

# 1. The Request Object
@dataclass
class ClaimShiftCommand:
    user_id: int
    master_slot_id: int
    time_block: str
    date: date

# 2. The Handler
class ClaimShiftHandler:
    def __init__(self, db: Session):
        self.db = db

    def execute(self, command: ClaimShiftCommand) -> BookedSlot:
        """Executes the command to save a claimed shift."""
        
        new_booking = BookedSlot(
            user_id=command.user_id,
            master_slot_id=command.master_slot_id,
            date=command.date,
            status=SlotStatus.to_contact,
            notes=f"Claimed {command.time_block} block."
        )
        
        self.db.add(new_booking)
        self.db.commit()
        self.db.refresh(new_booking)
        
        return new_booking