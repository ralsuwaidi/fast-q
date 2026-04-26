import calendar
from dataclasses import dataclass
from datetime import date

from sqlmodel import Session, select

from features.hospitals.models import MasterSlot
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
            select(BookedSlot, MasterSlot)
            .join(MasterSlot, BookedSlot.master_slot_id == MasterSlot.id, isouter=True)
            .where(BookedSlot.user_id == query.user.id)
        )
        results = self.db.exec(statement).all()

        user_events = {}
        for booked, master in results:
            title = master.physician if master else booked.custom_title
            specialty = master.specialty if master else "Custom"
            day = master.day_of_week if master else "Monday" 
            
            if day not in user_events:
                user_events[day] = []
                
            user_events[day].append({
                "name": f"{title} ({specialty})",
                "time": booked.notes.replace("Claimed ", "").replace(" block.", "") if booked.notes else "AM/PM",
                "status": booked.status
            })

        today = date.today()
        cal = calendar.Calendar(firstweekday=0) 
        month_days = cal.monthdatescalendar(today.year, today.month)
        flat_days = [day for week in month_days for day in week]
        
        calendar_days = []
        for d in flat_days:
            day_name = d.strftime("%A") 
            events_for_day = user_events.get(day_name, [])

            calendar_days.append({
                "date_obj": d,
                "day_str": str(d.day),         
                "datetime_str": d.isoformat(), 
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