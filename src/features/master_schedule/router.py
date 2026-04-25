from collections import defaultdict

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory=["src/features/master_schedule", "src/templates"])


def build_schedule(raw_slots):
    grouped = defaultdict(list)
    for slot in raw_slots:
        grouped[slot["day"]].append(slot)

    ordered_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    return {
        day: grouped.get(day, [])
        for day in ordered_days
        if day in grouped
    }


def render_calendar(request: Request, schedule_by_day, hospital_name: str):
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
        },
    )


# --- MGH ---
@router.get("/mgh", response_class=HTMLResponse)
async def mgh_schedule(request: Request):
    raw_slots = [
        {"id": 1, "day": "Monday", "specialty": "Epilepsy", "physician": "Dr. Dubeau", "time": "AM/PM", "email": "julie.gascon@muhc.mcgill.ca"},
        {"id": 2, "day": "Tuesday", "specialty": "Neuropsychiatry", "physician": "Dr. Kolivakis", "time": "PM", "email": "beatrice.stoklas@muhc.mcgill.ca"},
    ]

    return render_calendar(request, build_schedule(raw_slots), "MGH")


# --- MNH ---
@router.get("/mnh", response_class=HTMLResponse)
async def mnh_schedule(request: Request):
    raw_slots = [
        {"id": 3, "day": "Wednesday", "specialty": "Neuromuscular", "physician": "Dr. O'Ferral", "time": "AM/PM", "email": "erin.oferrall@mcgill.ca"},
        {"id": 4, "day": "Friday", "specialty": "Physiatry", "physician": "Dr. Trojan", "time": "AM/PM", "email": "beatrice.stoklas@muhc.mcgill.ca"},
    ]

    return render_calendar(request, build_schedule(raw_slots), "MNH")