from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from core.auth import get_current_user
from core.database import get_session
from features.hospitals.queries import (get_hospital_by_name,
                                        get_hospital_schedule)
from features.users.models import User

router = APIRouter()    
templates = Jinja2Templates(directory=["src/features/hospitals", "src/templates"])

def render_calendar(request: Request, schedule_by_day: dict, hospital_name: str, current_user: User | None):
    template_name = (
        "partials/public_calendar_content.html"
        if request.headers.get("hx-request")
        else "templates/public_calendar.html"
    )

    return templates.TemplateResponse(
        request=request,
        name=template_name,
        context={
            "schedule_by_day": schedule_by_day,
            "hospital_name": hospital_name,
            "current_user": current_user, # <-- Pass it to Jinja!
        },
    )
# --- MGH (Hospital A) ---
@router.get("/mgh", response_class=HTMLResponse)
async def mgh_schedule(
    request: Request, 
    db: Session = Depends(get_session),
    current_user: User | None = Depends(get_current_user)
):
    hospital = get_hospital_by_name(db, "Hospital A")

    if not hospital:
        return render_calendar(request, {}, "MGH (Not Found)", current_user)

    schedule = get_hospital_schedule(db, hospital.id)
    return render_calendar(request, schedule, "MGH Master Schedule", current_user)

# --- MNH (Hospital B) ---
@router.get("/mnh", response_class=HTMLResponse)
async def mnh_schedule(
    request: Request, 
    db: Session = Depends(get_session),
    current_user: User | None = Depends(get_current_user)
):
    hospital = get_hospital_by_name(db, "Hospital B")
    
    if not hospital:
        return render_calendar(request, {}, "MNH (Not Found)", current_user)

    schedule = get_hospital_schedule(db, hospital.id)
    return render_calendar(request, schedule, "MNH Master Schedule", current_user)