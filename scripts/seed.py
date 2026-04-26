import enum
from datetime import date, datetime, timezone

from pwdlib import PasswordHash
from pydantic import EmailStr
from sqlmodel import Field, Session, SQLModel, create_engine, select

# ==========================================
# 1. MODELS
# ==========================================
pwd_context = PasswordHash.recommended()
class UserRole(str, enum.Enum):
    admin = "admin"
    resident = "resident"

class User(SQLModel, table=True):
    """
    The core User database model.
    """
    id: int | None = Field(default=None, primary_key=True)
    email: EmailStr = Field(unique=True, index=True)
    hashed_password: str
    full_name: str | None = Field(default=None)
    role: UserRole = Field(default=UserRole.resident)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

class Hospital(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)

class MasterSlot(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hospital_id: int = Field(foreign_key="hospital.id")
    day_of_week: str
    specialty: str | None = Field(default=None) 
    physician: str
    time_block: str 
    contact_email: str

class SlotStatus(str, enum.Enum):
    to_contact = "To Contact"
    emailed = "Emailed"
    confirmed = "Confirmed"

class BookedSlot(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    master_slot_id: int | None = Field(default=None, foreign_key="masterslot.id")
    custom_title: str | None = Field(default=None)
    custom_location: str | None = Field(default=None)
    status: SlotStatus = Field(default=SlotStatus.to_contact)
    date: date
    notes: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ==========================================
# 2. DATABASE SETUP
# ==========================================

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True)


# ==========================================
# 3. SEEDING FUNCTION
# ==========================================

def seed_data():
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        if session.exec(select(User)).first():
            print("\n✅ Database already seeded. Exiting to prevent duplicates.")
            return

        print("\n🌱 Seeding Users...")
        
        # 2. Hash a standard password for your test users
        default_password = pwd_context.hash("password123") 
        
        admin = User(
            email="admin@muhc.ca", 
            hashed_password=default_password, 
            full_name="Admin Coordinator", 
            role=UserRole.admin,
            is_superuser=True
        )
        resident_1 = User(
            email="dr.smith@mcgill.ca", 
            hashed_password=default_password, 
            full_name="Dr. John Smith", 
            role=UserRole.resident
        )
        session.add_all([admin, resident_1])
        session.commit()

        print("🌱 Seeding Hospitals...")
        hosp_a = Hospital(name="Hospital A (MUHC)")
        hosp_b = Hospital(name="Hospital B (JGH)")
        session.add_all([hosp_a, hosp_b])
        session.commit()

        print("🌱 Seeding Master Schedule...")
        slots = [
            MasterSlot(hospital_id=hosp_a.id, day_of_week="Monday", specialty="Epilepsy", physician="Dr. Dubeau", time_block="AM/PM", contact_email="julie.gascon@muhc.mcgill.ca"),
            MasterSlot(hospital_id=hosp_a.id, day_of_week="Monday", specialty="Psychiatry", physician="Dr. Trounce", time_block="AM/PM", contact_email="beatrice.stoklas@muhc.mcgill.ca"),
            MasterSlot(hospital_id=hosp_a.id, day_of_week="Tuesday", specialty="Neuroinflammatory", physician="Dr. Harroud", time_block="AM/PM", contact_email="mariaangela.costa@muhc.mcgill.ca"),
            MasterSlot(hospital_id=hosp_b.id, day_of_week="Wednesday", specialty="Neuromuscular", physician="Dr. O'Ferral", time_block="AM", contact_email="erin.oferrall@mcgill.ca"),
            MasterSlot(hospital_id=hosp_b.id, day_of_week="Thursday", specialty="General Neurology", physician="Dr. Durcan", time_block="AM/PM", contact_email="jocelyn.bigot@muhc.mcgill.ca")
        ]
        session.add_all(slots)
        session.commit()

        print("🌱 Seeding Resident's Personal Bookings...")
        booking_1 = BookedSlot(
            user_id=resident_1.id, 
            master_slot_id=slots[0].id, 
            status=SlotStatus.to_contact,
            date=date(2026, 6, 10) 
        )
        booking_2 = BookedSlot(
            user_id=resident_1.id, 
            master_slot_id=slots[2].id, 
            status=SlotStatus.emailed,
            date=date(2026, 6, 21), 
            notes="Sent email asking for shadowing availability on Oct 12th."
        )
        booking_custom = BookedSlot(
            user_id=resident_1.id,
            master_slot_id=None, 
            custom_title="External Clinic Sync",
            custom_location="Downtown Medical Center",
            status=SlotStatus.confirmed,
            date=date(2026, 6, 22), 
            notes="Approved by Dr. Allen."
        )

        session.add_all([booking_1, booking_2, booking_custom])
        session.commit()
        
        print("\n🎉 Database successfully seeded with test data!")

if __name__ == "__main__":
    seed_data()