# src/features/residents/queries/get_calendar.py
import calendar
from dataclasses import dataclass
from datetime import date

from sqlmodel import Session, select

from features.users.models import User

from ..models import BookedSlot


@dataclass
class GetResidentCalendarQuery:
    user: User
    selected_date: date | None = None  # <--- 1. Add this field


class GetResidentCalendarHandler:
    def __init__(self, db: Session):
        self.db = db

    def execute(self, query: GetResidentCalendarQuery) -> dict:
        statement = select(BookedSlot).where(BookedSlot.user_id == query.user.id)
        results = self.db.exec(statement).all()

        user_events = {}
        for booked in results:
            title = booked.physician
            specialty = booked.specialty or "Custom"
            event_date_str = booked.date.isoformat() if booked.date else None
            if not event_date_str:
                continue
            if event_date_str not in user_events:
                user_events[event_date_str] = []

            user_events[event_date_str].append(
                {
                    "id": booked.id,
                    "name": f"{title} ({specialty})",
                    "time": booked.time_block,
                    "status": booked.status,
                }
            )

        today = date.today()
        # <--- 2. Determine which date is active (clicked day OR today)
        active_date = query.selected_date or today

        cal = calendar.Calendar(firstweekday=0)
        month_days = cal.monthdatescalendar(today.year, today.month)
        flat_days = [day for week in month_days for day in week]

        calendar_days = []
        for d in flat_days:
            date_str = d.isoformat()
            calendar_days.append(
                {
                    "date_obj": d,
                    "day_str": str(d.day),
                    "datetime_str": date_str,
                    "is_current_month": d.month == today.month,
                    "is_today": d == today,
                    "is_selected": d == active_date,  # <--- 3. Use active_date here
                    "events": user_events.get(date_str, []),
                }
            )

        return {
            "hospital_name": "My",
            "current_month_name": today.strftime("%B %Y"),
            "calendar_days": calendar_days,
            "selected_day_events": next(
                (d["events"] for d in calendar_days if d["is_selected"]), []
            ),
            "current_user": query.user,
        }
