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
        hospital_name = ""
        physician = ""
        specialty = ""
        contact_email = ""
        time_block = ""
        
        if query.master_slot_id:
            master_slot = self.db.get(MasterSlot, query.master_slot_id)
            if master_slot:
                physician = master_slot.physician
                specialty = master_slot.specialty or ""
                contact_email = master_slot.contact_email
                time_block = master_slot.time_block
                
                from features.hospitals.models import Hospital
                hospital = self.db.get(Hospital, master_slot.hospital_id)
                if hospital:
                    hospital_name = hospital.name
                
        return {
            "master_slot": master_slot,
            "hospital_name": hospital_name,
            "physician": physician,
            "specialty": specialty,
            "contact_email": contact_email,
            "time_block": time_block
        }