from dataclasses import dataclass
from datetime import date

from fastapi import HTTPException
from sqlmodel import Session

from features.hospitals.models import Hospital, MasterSlot

from ..models import BookedSlot, SlotStatus


@dataclass
class ClaimShiftCommand:
    user_id: int
    master_slot_id: int
    time_block: str
    date: date
    status: SlotStatus = SlotStatus.to_contact
    notes: str | None = None


class ClaimShiftHandler:
    """
    Books a shift derived from a MasterSlot. Hospital, physician, specialty,
    and contact email come from the master slot — never from user input — so
    the booking stays authoritative even if the form is tampered with.
    """

    def __init__(self, db: Session):
        self.db = db

    def execute(self, command: ClaimShiftCommand) -> BookedSlot:
        master = self.db.get(MasterSlot, command.master_slot_id)
        if master is None:
            raise HTTPException(status_code=404, detail="Master slot not found")

        hospital = self.db.get(Hospital, master.hospital_id)
        if hospital is None:
            raise HTTPException(status_code=404, detail="Hospital not found")

        booking = BookedSlot(
            user_id=command.user_id,
            hospital_name=hospital.name,
            date=command.date,
            specialty=master.specialty,
            physician=master.physician,
            time_block=command.time_block,
            contact_email=master.contact_email,
            status=command.status,
            notes=command.notes,
        )
        self.db.add(booking)
        self.db.commit()
        self.db.refresh(booking)
        return booking
