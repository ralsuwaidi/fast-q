from collections import defaultdict
from dataclasses import dataclass
from sqlmodel import Session, select
from features.hospitals.models import MasterSlot

@dataclass
class GetHospitalScheduleQuery:
    hospital_id: int

class GetHospitalScheduleHandler:
    def __init__(self, db: Session):
        self.db = db

    def execute(self, query: GetHospitalScheduleQuery) -> dict:
        """
        Fetches all slots for a specific hospital and groups them 
        by day of the week for the calendar UI.
        """
        db_slots = self.db.exec(select(MasterSlot).where(MasterSlot.hospital_id == query.hospital_id)).all()
        
        grouped = defaultdict(list)
        for slot in db_slots:
            grouped[slot.day_of_week].append({
                "id": slot.id,
                "day": slot.day_of_week,
                "specialty": slot.specialty,
                "physician": slot.physician,
                "time": slot.time_block,
                "email": slot.contact_email
            })

        ordered_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        return {
            day: grouped.get(day, [])
            for day in ordered_days
            if day in grouped
        }
