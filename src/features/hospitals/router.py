from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from fastapi import Form

from core.auth import get_current_user
from core.database import get_session
from features.hospitals.queries.get_hospital import GetHospitalByNameQuery, GetHospitalByNameHandler
from features.hospitals.queries.get_schedule import GetHospitalScheduleQuery, GetHospitalScheduleHandler
from features.hospitals.commands.create_hospital import CreateHospitalCommand, CreateHospitalHandler
from features.users.models import User
from features.hospitals.models import Hospital

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
    hospital = GetHospitalByNameHandler(db).execute(GetHospitalByNameQuery("Hospital A"))

    if not hospital:
        return render_calendar(request, {}, "MGH (Not Found)", current_user)

    schedule = GetHospitalScheduleHandler(db).execute(GetHospitalScheduleQuery(hospital.id))
    return render_calendar(request, schedule, "MGH Master Schedule", current_user)

# --- MNH (Hospital B) ---
@router.get("/mnh", response_class=HTMLResponse)
async def mnh_schedule(
    request: Request, 
    db: Session = Depends(get_session),
    current_user: User | None = Depends(get_current_user)
):
    hospital = GetHospitalByNameHandler(db).execute(GetHospitalByNameQuery("Hospital B"))
    
    if not hospital:
        return render_calendar(request, {}, "MNH (Not Found)", current_user)

    schedule = GetHospitalScheduleHandler(db).execute(GetHospitalScheduleQuery(hospital.id))
    return render_calendar(request, schedule, "MNH Master Schedule", current_user)

@router.get("/hospitals/{hospital_id}", response_class=HTMLResponse)
async def dynamic_hospital_schedule(
    hospital_id: int,
    request: Request, 
    db: Session = Depends(get_session),
    current_user: User | None = Depends(get_current_user)
):
    hospital = db.get(Hospital, hospital_id)
    if not hospital:
        return render_calendar(request, {}, "Hospital Not Found", current_user)

    schedule = GetHospitalScheduleHandler(db).execute(GetHospitalScheduleQuery(hospital.id))
    return render_calendar(request, schedule, f"{hospital.name} Master Schedule", current_user)

@router.post("/hospitals/new", response_class=HTMLResponse)
async def create_hospital(
    request: Request,
    name: str = Form(...),
    db: Session = Depends(get_session),
    current_user: User | None = Depends(get_current_user)
):
    command = CreateHospitalCommand(name=name)
    hospital = CreateHospitalHandler(db).execute(command)
    
    response = HTMLResponse()
    response.headers["HX-Redirect"] = "/dashboard"
    return response