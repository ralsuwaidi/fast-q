# src/features/residents/queries/get_custom_slot_form.py
from dataclasses import dataclass

from sqlmodel import Session

# Note: Assuming MasterSlot is imported from here based on your previous code
from features.hospitals.models import MasterSlot


@dataclass
class GetCustomSlotFormQuery:
    master_slot_id: int | None

class GetCustomSlotFormHandler:
    def __init__(self, db: Session):
        self.db = db

    def execute(self, query: GetCustomSlotFormQuery) -> dict:
        """Fetches necessary data to populate the custom slot form."""
        
        master_slot = None
        hospital_name = None
        
        if query.master_slot_id:
            master_slot = self.db.get(MasterSlot, query.master_slot_id)
            if master_slot and master_slot.hospital:
                hospital_name = master_slot.hospital.name
                
        return {
            "master_slot": master_slot,
            "hospital_name": hospital_name
        }