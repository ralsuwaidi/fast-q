from datetime import date

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from core.auth import get_current_user
from core.database import get_session
from features.residents.commands.claim_shift import (ClaimShiftCommand,
                                                     ClaimShiftHandler)
from features.residents.queries.get_calendar import (
    GetResidentCalendarHandler, GetResidentCalendarQuery)
from features.users.models import User

router = APIRouter()
templates = Jinja2Templates(directory=["src/features/residents", "src/templates"])

@router.get("/my-calendar", response_class=HTMLResponse)
async def home_page(
    request: Request,
    db: Session = Depends(get_session),
    current_user: User | None = Depends(get_current_user)
):
    if not current_user:
        return HTMLResponse("Please log in to view your calendar.", status_code=401)

    # 1. Create the Query
    query = GetResidentCalendarQuery(user=current_user)
    
    # 2. Execute via Handler
    handler = GetResidentCalendarHandler(db)
    template_context = handler.execute(query)

    return templates.TemplateResponse(
        request=request, 
        name="templates/calendar.html",
        context=template_context
    )


@router.post("/my-calendar/claim/{master_slot_id}", response_class=HTMLResponse)
async def claim_shift(
    master_slot_id: int, 
    time_block: str = Query(...), 
    selected_date: date = Query(...),
    db: Session = Depends(get_session),
    current_user: User | None = Depends(get_current_user)
):
    if not current_user:
        return HTMLResponse("<span class='text-red-500 text-xs'>Please log in</span>", status_code=401)

    # 1. Create the Command
    command = ClaimShiftCommand(
        user_id=current_user.id,
        master_slot_id=master_slot_id,
        time_block=time_block,
        date=selected_date
    )
    
    # 2. Execute via Handler
    handler = ClaimShiftHandler(db)
    handler.execute(command)

    res = Response(
        content=f"""
        <span class="inline-flex items-center rounded-full bg-green-50 px-2.5 py-0.5 text-xs font-semibold text-green-700">
            ✓ Added {time_block}
        </span>
        """,
        media_type="text/html"
    )

    res.headers["HX-Trigger"] = "calendarUpdated"

    return res
