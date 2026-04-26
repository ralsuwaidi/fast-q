from datetime import date

from fastapi import APIRouter, Depends, Query, Request, Form
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from core.auth import get_current_user
from core.database import get_session
from features.residents.commands.claim_shift import (ClaimShiftCommand,
                                                     ClaimShiftHandler)
from features.residents.queries.get_calendar import (
    GetResidentCalendarHandler, GetResidentCalendarQuery)
from features.residents.models import BookedSlot, SlotStatus
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
        return Response(status_code=302, headers={"Location": "/login"})

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


@router.get("/my-calendar/custom-slot/new", response_class=HTMLResponse)
async def get_custom_slot_drawer(
    request: Request,
    master_slot_id: int | None = Query(None),
    time_block: str | None = Query(None),
    selected_date: date | None = Query(None),
    db: Session = Depends(get_session)
):
    from features.hospitals.models import MasterSlot
    
    master_slot = None
    if master_slot_id:
        master_slot = db.get(MasterSlot, master_slot_id)
        
    return templates.TemplateResponse(
        request=request,
        name="templates/partials/add_custom_slot_drawer.html",
        context={
            "master_slot": master_slot,
            "hospital_name": master_slot.hospital.name if master_slot and master_slot.hospital else None,
            "master_slot_id": master_slot_id,
            "time_block_override": time_block,
            "selected_date": selected_date
        }
    )

@router.post("/my-calendar/custom-slot", response_class=HTMLResponse)
async def create_custom_slot(
    request: Request,
    hospital_name: str = Form(...),
    physician: str = Form(...),
    time_block: str = Form(...),
    contact_email: str = Form(...),
    date: date = Form(...),
    specialty: str | None = Form(None),
    status: SlotStatus = Form(SlotStatus.to_contact),
    notes: str | None = Form(None),
    db: Session = Depends(get_session),
    current_user: User | None = Depends(get_current_user)
):
    if not current_user:
        return HTMLResponse("<span class='text-red-500 text-xs'>Please log in</span>", status_code=401)
        
    slot = BookedSlot(
        user_id=current_user.id,
        hospital_name=hospital_name,
        physician=physician,
        time_block=time_block,
        contact_email=contact_email,
        date=date,
        specialty=specialty,
        status=status,
        notes=notes
    )
    db.add(slot)
    db.commit()
    
    html_content = """
    <div class='p-4 text-green-600 font-semibold text-center'>
        <svg class="mx-auto size-12 text-green-500 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        Slot created successfully!
    </div>
    <script>
        setTimeout(() => {
            const drawer = document.getElementById("add-custom-slot-drawer");
            if (drawer) drawer.close();
            window.location.reload();
        }, 1200);
    </script>
    """
    return HTMLResponse(content=html_content)
