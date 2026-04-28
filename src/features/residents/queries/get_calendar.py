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
    selected_date: date | None = None
    view_date: date | None = None


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
        # 2. Determine which month the calendar grid should draw
        view_date = query.view_date or query.selected_date or today
        # 3. Determine which day should have the blue highlight
        active_date = query.selected_date or today

        # 4. Calculate Previous and Next Months (handles year rollovers)
        if view_date.month == 1:
            prev_month = date(view_date.year - 1, 12, 1)
        else:
            prev_month = date(view_date.year, view_date.month - 1, 1)

        if view_date.month == 12:
            next_month = date(view_date.year + 1, 1, 1)
        else:
            next_month = date(view_date.year, view_date.month + 1, 1)

        cal = calendar.Calendar(firstweekday=0)
        # 5. Build grid based on VIEW date, not today
        month_days = cal.monthdatescalendar(view_date.year, view_date.month)

        flat_days = [day for week in month_days for day in week]

        calendar_days = []
        for d in flat_days:
            date_str = d.isoformat()
            calendar_days.append(
                {
                    "date_obj": d,
                    "day_str": str(d.day),
                    "datetime_str": date_str,
                    "is_current_month": d.month == view_date.month,  # Update this check
                    "is_today": d == today,
                    "is_selected": d == active_date,
                    "events": user_events.get(date_str, []),
                }
            )

        return {
            "hospital_name": "My",
            "current_month_name": view_date.strftime("%B %Y"),
            "current_view_date": view_date.isoformat(),  # Pass current view back
            "prev_month_date": prev_month.isoformat(),
            "next_month_date": next_month.isoformat(),
            "calendar_days": calendar_days,
            "selected_day_events": next(
                (d["events"] for d in calendar_days if d["is_selected"]), []
            ),
            "current_user": query.user,
        }
