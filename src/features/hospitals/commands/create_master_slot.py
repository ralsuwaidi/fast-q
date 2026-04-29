from dataclasses import dataclass
from sqlmodel import Session
from features.hospitals.models import MasterSlot

@dataclass
class CreateMasterSlotCommand:
    hospital_id: int
    day_of_week: str
    physician: str
    time_block: str
    contact_email: str
    specialty: str | None = None

class CreateMasterSlotHandler:
    def __init__(self, db: Session):
        self.db = db

    def execute(self, command: CreateMasterSlotCommand) -> MasterSlot:
        """
        COMMAND: Creates a new shift on the master schedule.
        """
        new_slot = MasterSlot(
            hospital_id=command.hospital_id,
            day_of_week=command.day_of_week,
            physician=command.physician,
            time_block=command.time_block,
            contact_email=command.contact_email,
            specialty=command.specialty
        )
        self.db.add(new_slot)
        self.db.commit()
        self.db.refresh(new_slot)
        
        return new_slot
