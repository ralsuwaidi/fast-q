from collections import defaultdict

from sqlmodel import Session, select

from features.hospitals.models import Hospital, MasterSlot


def get_hospital_by_name(db: Session, partial_name: str) -> Hospital | None:
    """Fetches a hospital by a partial string match."""
    return db.exec(select(Hospital).where(Hospital.name.contains(partial_name))).first()

def get_hospital_schedule(db: Session, hospital_id: int) -> dict:
    """
    Fetches all slots for a specific hospital and groups them 
    by day of the week for the calendar UI.
    """
    db_slots = db.exec(select(MasterSlot).where(MasterSlot.hospital_id == hospital_id)).all()
    
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