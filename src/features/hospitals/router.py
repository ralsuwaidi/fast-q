from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from core.auth import get_current_user
from core.database import get_session
from features.hospitals.commands.create_hospital import (
    CreateHospitalCommand,
    CreateHospitalHandler,
)
from features.hospitals.models import Hospital
from features.hospitals.queries.get_schedule import (
    GetHospitalScheduleHandler,
    GetHospitalScheduleQuery,
)
from features.users.models import User

router = APIRouter()
templates = Jinja2Templates(directory=["src/features/hospitals", "src/templates"])


@router.get("/hospitals/nav", response_class=HTMLResponse)
async def hospital_nav_list(
    request: Request, 
    active_short_name: str | None = None,
    db: Session = Depends(get_session)
):
    hospitals = db.exec(select(Hospital)).all()
    # Prioritize the passed short_name, fall back to URL detection
    current_url = request.headers.get("HX-Current-URL", "")
    
    html = ""
    for hospital in hospitals:
        is_active = (active_short_name == hospital.short_name) or (f"/hospitals/{hospital.short_name}" in current_url)
        
        # Use more distinct active classes
        if is_active:
            active_classes = "bg-indigo-600 text-white shadow-sm"
            icon_classes = "border-indigo-200 bg-indigo-500 text-white"
        else:
            active_classes = "text-gray-700 hover:bg-gray-50 hover:text-indigo-600 dark:text-gray-400 dark:hover:bg-white/5 dark:hover:text-white"
            icon_classes = "border-gray-200 bg-white text-gray-400 group-hover:border-indigo-600 group-hover:text-indigo-600 dark:border-white/10 dark:bg-white/5 dark:group-hover:border-white/20 dark:group-hover:text-white"

        html += f"""
        <li>
            <a href="/hospitals/{hospital.short_name}" 
               hx-get="/hospitals/{hospital.short_name}" 
               hx-target="#main-content" 
               hx-swap="innerHTML transition:true" 
               hx-push-url="true"
               onclick="document.getElementById('sidebar').close()"
               class="group flex gap-x-3 rounded-md p-2 text-sm font-semibold {active_classes}">
                <span class="flex size-6 shrink-0 items-center justify-center rounded-lg border text-[0.625rem] font-medium {icon_classes}">
                    {hospital.name[0].upper()}
                </span>
                <span class="truncate">{hospital.name}</span>
            </a>
        </li>
        """
    return HTMLResponse(content=html)


def render_calendar(
    request: Request,
    schedule_by_day: dict,
    hospital_name: str,
    current_user: User | None,
):
    template_name = (
        "templates/partials/public_calendar_content.html"
        if request.headers.get("hx-request")
        else "templates/public_calendar.html"
    )

    return templates.TemplateResponse(
        request=request,
        name=template_name,
        context={
            "schedule_by_day": schedule_by_day,
            "hospital_name": hospital_name,
            "current_user": current_user,
        },
    )


@router.get("/hospitals/{short_name}", response_class=HTMLResponse)
async def hospital_schedule_by_short_name(
    short_name: str,
    request: Request,
    db: Session = Depends(get_session),
    current_user: User | None = Depends(get_current_user),
):
    # Find hospital by short_name
    hospital = db.exec(
        select(Hospital).where(Hospital.short_name == short_name)
    ).first()

    if not hospital:
        return render_calendar(
            request, {}, f"{short_name.upper()} (Not Found)", current_user
        )

    schedule = GetHospitalScheduleHandler(db).execute(
        GetHospitalScheduleQuery(hospital.id)
    )
    
    response = render_calendar(
        request, schedule, f"{hospital.name} Master Schedule", current_user
    )
    # Pass the short_name in the trigger so the nav knows exactly what to highlight
    import json
    response.headers["HX-Trigger"] = json.dumps({"hospitalSelected": {"short_name": short_name}})
    return response


@router.post("/hospitals/new", response_class=HTMLResponse)
async def create_hospital(
    request: Request,
    name: str = Form(...),
    short_name: str = Form(...),
    db: Session = Depends(get_session),
    current_user: User | None = Depends(get_current_user),
):
    command = CreateHospitalCommand(name=name, short_name=short_name)
    hospital = CreateHospitalHandler(db).execute(command)

    response = HTMLResponse()
    response.headers["HX-Redirect"] = "/dashboard"
    return response
