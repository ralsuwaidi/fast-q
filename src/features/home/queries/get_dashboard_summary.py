from collections import defaultdict
from dataclasses import dataclass
from datetime import date

from sqlmodel import Session, select

from features.hospitals.models import Hospital, MasterSlot
from features.residents.models import BookedSlot, SlotStatus
from features.users.models import User


@dataclass
class GetDashboardSummaryQuery:
    current_user: User | None


@dataclass
class HospitalSummary:
    id: int
    name: str
    short_name: str
    slot_count: int
    has_my_bookings: bool


@dataclass
class MySummary:
    upcoming_count: int
    dot: str | None  # "success" | "warning" | "danger" | None


@dataclass
class DashboardSummary:
    hospitals: list[HospitalSummary]
    my: MySummary | None
    user_count: int


class GetDashboardSummaryHandler:
    def __init__(self, db: Session):
        self.db = db

    def execute(self, query: GetDashboardSummaryQuery) -> DashboardSummary:
        hospitals = self.db.exec(select(Hospital)).all()
        slots = self.db.exec(select(MasterSlot)).all()

        slot_counts: dict[int, int] = defaultdict(int)
        for slot in slots:
            slot_counts[slot.hospital_id] += 1

        my_hospital_names: set[str] = set()
        my_summary: MySummary | None = None

        if query.current_user:
            my_slots = self.db.exec(
                select(BookedSlot).where(BookedSlot.user_id == query.current_user.id)
            ).all()
            today = date.today()
            upcoming = [s for s in my_slots if s.date >= today]
            my_hospital_names = {s.hospital_name for s in my_slots}

            dot: str | None = None
            if upcoming:
                statuses = {s.status for s in upcoming}
                overdue = any(
                    s.date < today and s.status != SlotStatus.confirmed
                    for s in my_slots
                )
                if overdue:
                    dot = "danger"
                elif SlotStatus.to_contact in statuses:
                    dot = "warning"
                elif statuses == {SlotStatus.confirmed}:
                    dot = "success"
                else:
                    dot = "warning"

            my_summary = MySummary(upcoming_count=len(upcoming), dot=dot)

        hospital_summaries = [
            HospitalSummary(
                id=h.id,
                name=h.name,
                short_name=h.short_name,
                slot_count=slot_counts.get(h.id, 0),
                has_my_bookings=h.name in my_hospital_names,
            )
            for h in hospitals
        ]

        user_count = 0
        if query.current_user and query.current_user.role.value == "admin":
            user_count = len(self.db.exec(select(User)).all())

        return DashboardSummary(
            hospitals=hospital_summaries,
            my=my_summary,
            user_count=user_count,
        )
