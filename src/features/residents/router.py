# src/features/residents/router.py
from datetime import date as ddate

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from core.auth import get_current_user
from core.database import get_session
from features.residents.commands.create_custom_slot import (
    CreateCustomSlotCommand,
    CreateCustomSlotHandler,
)
from features.residents.commands.delete_slot import DeleteSlotCommand, DeleteSlotHandler
from features.residents.models import SlotStatus
from features.residents.queries.get_calendar import (
    GetResidentCalendarHandler,
    GetResidentCalendarQuery,
)
from features.residents.queries.get_custom_slot_form import (
    GetCustomSlotFormHandler,
    GetCustomSlotFormQuery,
)
from features.residents.queries.get_slot_details import (
    GetSlotDetailsHandler,
    GetSlotDetailsQuery,
)
from features.users.models import User

from features.residents.commands.update_slot import UpdateSlotCommand, UpdateSlotHandler

router = APIRouter()
templates = Jinja2Templates(directory=["src/features/residents", "src/templates"])


@router.get("/my-calendar/slots/{slot_id}/edit", response_class=HTMLResponse)
async def get_edit_slot_page(
    slot_id: int,
    request: Request,
    db: Session = Depends(get_session),
    current_user: User | None = Depends(get_current_user),
):
    if not current_user:
        return Response(status_code=302, headers={"Location": "/login"})

    is_htmx = request.headers.get("hx-request") == "true"
    
    query = GetSlotDetailsQuery(slot_id=slot_id, user_id=current_user.id)
    slot = GetSlotDetailsHandler(db).execute(query)

    template_name = (
        "templates/partials/add_custom_slot_content.html"
        if is_htmx
        else "templates/add_custom_slot.html"
    )

    return templates.TemplateResponse(
        request=request,
        name=template_name,
        context={
            "slot": slot,
            "hospital_name": slot.hospital_name,
            "physician": slot.physician,
            "specialty": slot.specialty,
            "contact_email": slot.contact_email,
            "time_block_override": slot.time_block,
            "selected_date": slot.date,
            "status": slot.status,
            "notes": slot.notes,
        },
    )


@router.post("/my-calendar/slots/{slot_id}/edit", response_class=HTMLResponse)
async def update_slot_route(
    slot_id: int,
    request: Request,
    hospital_name: str = Form(...),
    physician: str = Form(...),
    time_block: str = Form(...),
    contact_email: str = Form(...),
    date: str = Form(...),
    specialty: str | None = Form(None),
    status: SlotStatus = Form(SlotStatus.to_contact),
    notes: str | None = Form(None),
    db: Session = Depends(get_session),
    current_user: User | None = Depends(get_current_user),
):
    if not current_user:
        return HTMLResponse("Unauthorized", status_code=401)

    parsed_date = ddate.fromisoformat(date)
    
    command = UpdateSlotCommand(
        slot_id=slot_id,
        user_id=current_user.id,
        hospital_name=hospital_name,
        physician=physician,
        time_block=time_block,
        contact_email=contact_email,
        date=parsed_date,
        specialty=specialty,
        status=status,
        notes=notes,
    )
    UpdateSlotHandler(db).execute(command)

    is_htmx = request.headers.get("hx-request") == "true"
    if is_htmx:
        response = HTMLResponse()
        response.headers["HX-Redirect"] = "/my-calendar"
        return response
    
    return Response(status_code=302, headers={"Location": "/my-calendar"})


# src/features/residents/router.py


@router.get("/my-calendar", response_class=HTMLResponse)
async def home_page(
    request: Request,
    selected_date: ddate | None = Query(None),
    view_date: ddate | None = Query(None),
    db: Session = Depends(get_session),
    current_user: User | None = Depends(get_current_user),
):
    if not current_user:
        return Response(status_code=302, headers={"Location": "/login"})

    # 1. Detect if this is an HTMX request
    is_htmx = request.headers.get("hx-request") == "true"

    query = GetResidentCalendarQuery(
        user=current_user, selected_date=selected_date, view_date=view_date
    )
    template_context = GetResidentCalendarHandler(db).execute(query)

    # 2. Choose the template based on the request type
    template_name = (
        "templates/partials/my_calendar_content.html"
        if is_htmx
        else "templates/calendar.html"
    )

    response = templates.TemplateResponse(
        request=request, name=template_name, context=template_context
    )
    response.headers["HX-Trigger"] = "hospitalSelected"
    return response


@router.get("/my-calendar/custom-slot/new", response_class=HTMLResponse)
async def get_custom_slot_drawer(
    request: Request,
    master_slot_id: int | None = Query(None),
    time_block: str | None = Query(None),
    selected_date: ddate | None = Query(None),
    db: Session = Depends(get_session),
):
    is_htmx = request.headers.get("hx-request") == "true"

    # Dispatch Query
    query = GetCustomSlotFormQuery(master_slot_id=master_slot_id)
    form_data = GetCustomSlotFormHandler(db).execute(query)

    template_name = (
        "templates/partials/add_custom_slot_content.html"
        if is_htmx
        else "templates/add_custom_slot.html"
    )

    return templates.TemplateResponse(
        request=request,
        name=template_name,
        context={
            "master_slot": form_data["master_slot"],
            "hospital_name": form_data["hospital_name"],
            "physician": form_data["physician"],
            "specialty": form_data["specialty"],
            "contact_email": form_data["contact_email"],
            "master_slot_id": master_slot_id,
            "time_block_override": time_block or form_data["time_block"],
            "selected_date": selected_date,
        },
    )


@router.post("/my-calendar", response_class=HTMLResponse)
async def create_custom_slot(
    request: Request,
    hospital_name: str | None = Form(None),
    physician: str | None = Form(None),
    time_block: str | None = Form(None),
    contact_email: str | None = Form(None),
    date: str | None = Form(None),
    specialty: str | None = Form(None),
    status: SlotStatus = Form(SlotStatus.to_contact),
    notes: str | None = Form(None),
    db: Session = Depends(get_session),
    current_user: User | None = Depends(get_current_user),
):
    if not current_user:
        return HTMLResponse(
            "<span class='text-red-500 text-xs'>Please log in</span>", status_code=401
        )

    # --- 1. Router Level Validation ---
    errors = []
    if not hospital_name:
        errors.append("Hospital is required.")
    if not physician:
        errors.append("Physician is required.")
    if not time_block:
        errors.append("Time Block is required.")
    if not contact_email:
        errors.append("Contact Email is required.")
    if not date:
        errors.append("Date is required.")

    parsed_date = None
    if date:
        try:
            parsed_date = ddate.fromisoformat(date)
        except ValueError:
            errors.append("Invalid date format.")

    if errors:
        error_html = (
            "<div class='mb-4 p-3 bg-red-50 text-red-700 text-sm rounded-md border border-red-200'>"
            + "<br>".join(errors)
            + "</div>"
        )
        return templates.TemplateResponse(
            request=request,
            name="templates/partials/add_custom_slot_content.html",
            context={
                "hospital_name": hospital_name,
                "physician": physician,
                "specialty": specialty,
                "contact_email": contact_email,
                "selected_date": parsed_date,
                "time_block_override": time_block,
                "error_message": error_html,
            },
        )

    # --- 2. Dispatch Command (Write) ---
    command = CreateCustomSlotCommand(
        user_id=current_user.id,
        hospital_name=hospital_name,
        physician=physician,
        time_block=time_block,
        contact_email=contact_email,
        date=parsed_date,
        specialty=specialty,
        status=status,
        notes=notes,
    )
    CreateCustomSlotHandler(db).execute(command)

    # --- 3. Return Response (Redirect to Calendar) ---
    is_htmx = request.headers.get("hx-request") == "true"
    if is_htmx:
        response = HTMLResponse()
        response.headers["HX-Redirect"] = "/my-calendar"
        return response
    
    return Response(status_code=302, headers={"Location": "/my-calendar"})


@router.delete("/my-calendar/slots/{slot_id}", response_class=HTMLResponse)
async def delete_slot(
    slot_id: int,
    request: Request,
    db: Session = Depends(get_session),
    current_user: User | None = Depends(get_current_user),
):
    if not current_user:
        return HTMLResponse("Unauthorized", status_code=401)

    # 1. Execute Delete Command
    command = DeleteSlotCommand(slot_id=slot_id, user_id=current_user.id)
    DeleteSlotHandler(db).execute(command)

    # 2. Return Response (Redirect to Calendar)
    is_htmx = request.headers.get("hx-request") == "true"
    if is_htmx:
        response = HTMLResponse()
        response.headers["HX-Redirect"] = "/my-calendar"
        # Optional: Trigger a toast notification specifically for deletion
        response.headers["HX-Trigger"] = "slotDeleted"
        return response
    
    return Response(status_code=302, headers={"Location": "/my-calendar"})


@router.get("/my-calendar/slots/{slot_id}/details", response_class=HTMLResponse)
async def view_slot_details(
    slot_id: int,
    request: Request,
    db: Session = Depends(get_session),
    current_user: User | None = Depends(get_current_user),
):
    if not current_user:
        return HTMLResponse("Unauthorized", status_code=401)

    try:
        # Dispatch Query
        query = GetSlotDetailsQuery(slot_id=slot_id, user_id=current_user.id)
        slot = GetSlotDetailsHandler(db).execute(query)
    except HTTPException:
        return HTMLResponse(
            "<div class='p-4 text-red-500'>Slot not found or unauthorized.</div>",
            status_code=404,
        )

    return templates.TemplateResponse(
        request=request,
        name="templates/partials/view_slot_drawer.html",
        context={"slot": slot},
    )
