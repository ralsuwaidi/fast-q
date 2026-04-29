from dataclasses import dataclass
from sqlmodel import Session, select
from features.hospitals.models import Hospital

@dataclass
class GetAllHospitalsQuery:
    pass

class GetAllHospitalsHandler:
    def __init__(self, db: Session):
        self.db = db

    def execute(self, query: GetAllHospitalsQuery) -> list[Hospital]:
        """Fetches all hospitals."""
        return self.db.exec(select(Hospital)).all()
