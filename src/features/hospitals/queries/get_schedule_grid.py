from collections import OrderedDict
from dataclasses import dataclass

from sqlmodel import Session, select

from features.hospitals.models import MasterSlot

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
SESSIONS = ["AM", "PM"]


@dataclass
class GetScheduleGridQuery:
    hospital_id: int


@dataclass
class GridCellSlot:
    physician: str
    qualifier: str | None


@dataclass
class GridRow:
    session: str
    days: dict[str, list[GridCellSlot]]


@dataclass
class GridSpecialty:
    name: str
    contact_email: str | None
    rows: list[GridRow]


@dataclass
class ScheduleGrid:
    days: list[str]
    specialties: list[GridSpecialty]


class GetScheduleGridHandler:
    def __init__(self, db: Session):
        self.db = db

    def execute(self, query: GetScheduleGridQuery) -> ScheduleGrid:
        slots = self.db.exec(
            select(MasterSlot).where(MasterSlot.hospital_id == query.hospital_id)
        ).all()

        # specialty -> session -> day -> [slots]
        grouped: "OrderedDict[str, dict[str, dict[str, list[GridCellSlot]]]]" = (
            OrderedDict()
        )
        contacts: dict[str, str] = {}
        first_seen_order: list[str] = []

        for slot in slots:
            specialty = (slot.specialty or "Other").upper()
            if specialty not in grouped:
                grouped[specialty] = {s: {d: [] for d in DAYS} for s in SESSIONS}
                first_seen_order.append(specialty)
            session = slot.session if slot.session in SESSIONS else "AM"
            day = slot.day_of_week
            if day in DAYS:
                grouped[specialty][session][day].append(
                    GridCellSlot(physician=slot.physician, qualifier=slot.qualifier)
                )
            if specialty not in contacts and slot.contact_email:
                contacts[specialty] = slot.contact_email

        specialties: list[GridSpecialty] = []
        for name in first_seen_order:
            sessions = grouped[name]
            rows: list[GridRow] = []
            for s in SESSIONS:
                if any(sessions[s][d] for d in DAYS):
                    rows.append(GridRow(session=s, days=sessions[s]))
            specialties.append(
                GridSpecialty(
                    name=name, contact_email=contacts.get(name), rows=rows
                )
            )

        return ScheduleGrid(days=DAYS, specialties=specialties)
