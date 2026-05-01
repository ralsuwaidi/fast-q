from dataclasses import dataclass
from sqlmodel import Session
from features.hospitals.models import Hospital

@dataclass
class CreateHospitalCommand:
    name: str
    short_name: str

class CreateHospitalHandler:
    def __init__(self, db: Session):
        self.db = db

    def execute(self, command: CreateHospitalCommand) -> Hospital:
        if " " in command.short_name:
            raise ValueError("Short name cannot contain spaces")
        hospital = Hospital(name=command.name, short_name=command.short_name)
        self.db.add(hospital)
        self.db.commit()
        self.db.refresh(hospital)
        return hospital
