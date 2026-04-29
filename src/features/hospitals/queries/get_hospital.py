from dataclasses import dataclass
from sqlmodel import Session, select
from features.hospitals.models import Hospital

@dataclass
class GetHospitalByNameQuery:
    partial_name: str

class GetHospitalByNameHandler:
    def __init__(self, db: Session):
        self.db = db

    def execute(self, query: GetHospitalByNameQuery) -> Hospital | None:
        """Fetches a hospital by a partial string match."""
        return self.db.exec(select(Hospital).where(Hospital.name.contains(query.partial_name))).first()
