import calendar
from dataclasses import dataclass
from datetime import date

from sqlmodel import Session, select

from features.users.models import User

from ..models import BookedSlot


# 1. The Request Object
@dataclass
class GetResidentCalendarQuery:
    user: User

# 2. The Handler
class GetResidentCalendarHandler:
    def __init__(self, db: Session):
        self.db = db

    def execute(self, query: GetResidentCalendarQuery) -> dict:
        """Executes the query to build the calendar context."""
        
        statement = (
            select(BookedSlot)
            .where(BookedSlot.user_id == query.user.id)
        )
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
            
            time_str = booked.time_block
                
            user_events[event_date_str].append({
                "name": f"{title} ({specialty})",
                "time": time_str,
                "id": booked.id,
                "status": booked.status
            })

        today = date.today()
        cal = calendar.Calendar(firstweekday=0) 
        month_days = cal.monthdatescalendar(today.year, today.month)
        flat_days = [day for week in month_days for day in week]
        
        calendar_days = []
        for d in flat_days:
            date_str = d.isoformat()
            events_for_day = user_events.get(date_str, [])

            calendar_days.append({
                "date_obj": d,
                "day_str": str(d.day),         
                "datetime_str": date_str, 
                "is_current_month": d.month == today.month,
                "is_today": d == today,
                "is_selected": d == today,
                "events": events_for_day
            })

        return {
            "hospital_name": "My",
            "current_month_name": today.strftime("%B %Y"),
            "calendar_days": calendar_days,
            "selected_day_events": next((d["events"] for d in calendar_days if d["is_selected"]), []),
            "current_user": query.user
        }