import pytest
from fastapi.testclient import TestClient
from main import app
from core.auth import get_current_user
from features.users.models import User
from sqlmodel import SQLModel, Session, create_engine
from core.database import get_session
from features.residents.models import BookedSlot
from features.hospitals.models import MasterSlot
from sqlalchemy.pool import StaticPool

# Setup in-memory sqlite for testing
engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
SQLModel.metadata.create_all(engine)

def override_get_session():
    with Session(engine) as db:
        yield db

# Mock a user
mock_user = User(
    id=1,
    email="test@user.com",
    hashed_password="hashed_password",
    full_name="Test User",
    hospital_name="Test Hospital"
)

def override_get_current_user():
    return mock_user

app.dependency_overrides[get_session] = override_get_session
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)

def test_create_custom_slot_missing_fields():
    # Test POST /my-calendar/custom-slot with missing fields
    response = client.post(
        "/my-calendar/custom-slot",
        data={
            # Missing some required fields like date, time_block, etc.
            "hospital_name": "Test Hospital"
        }
    )
    assert response.status_code == 200
    # Should render the template with error message
    assert "Date is required." in response.text
    assert "Physician is required." in response.text

def test_create_custom_slot_success():
    # Test POST /my-calendar/custom-slot with all required fields
    response = client.post(
        "/my-calendar/custom-slot",
        data={
            "hospital_name": "My Hospital",
            "physician": "Dr. Smith",
            "time_block": "AM",
            "contact_email": "smith@test.com",
            "date": "2026-04-25",
            "specialty": "Cardiology",
            "status": "To Contact",
            "notes": "Test notes"
        }
    )
    assert response.status_code == 200
    # Should render success message
    assert "Slot created successfully!" in response.text

    # Verify it was inserted in the db
    with Session(engine) as db:
        from features.residents.models import BookedSlot
        slot = db.query(BookedSlot).filter(BookedSlot.physician == "Dr. Smith").first()
        assert slot is not None
        assert slot.date.isoformat() == "2026-04-25"
        assert slot.time_block == "AM"
