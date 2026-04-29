from dataclasses import dataclass
from sqlmodel import Session
from features.hospitals.models import Hospital

@dataclass
class CreateHospitalCommand:
    name: str

class CreateHospitalHandler:
    def __init__(self, db: Session):
        self.db = db

    def execute(self, command: CreateHospitalCommand) -> Hospital:
        hospital = Hospital(name=command.name)
        self.db.add(hospital)
        self.db.commit()
        self.db.refresh(hospital)
        return hospital
