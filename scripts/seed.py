import enum
from datetime import UTC, date, datetime

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
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Hospital(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    short_name: str = Field(unique=True, index=True, max_length=50)


class MasterSlot(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hospital_id: int = Field(foreign_key="hospital.id")
    day_of_week: str
    specialty: str | None = Field(default=None)
    physician: str
    time_block: str
    contact_email: str
    session: str = Field(default="AM")
    qualifier: str | None = Field(default=None)


class SlotStatus(str, enum.Enum):
    to_contact = "To Contact"
    emailed = "Emailed"
    confirmed = "Confirmed"


class BookedSlot(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    hospital_name: str
    date: date
    specialty: str | None = Field(default=None)
    physician: str
    time_block: str
    contact_email: str
    status: SlotStatus = Field(default=SlotStatus.to_contact)
    notes: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


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
            email="admin@example.com",
            hashed_password=default_password,
            full_name="Admin Coordinator",
            role=UserRole.admin,
            is_superuser=True,
        )
        resident_1 = User(
            email="resident@example.com",
            hashed_password=default_password,
            full_name="Dr. John Smith",
            role=UserRole.resident,
        )
        session.add_all([admin, resident_1])
        session.commit()

        print("🌱 Seeding Hospitals...")
        mgh = Hospital(name="Montreal General Hospital", short_name="MGH")
        mnh = Hospital(name="Montreal Neurological Hospital", short_name="MNH")
        session.add_all([mgh, mnh])
        session.commit()

        print("🌱 Seeding MGH Master Schedule...")

        def slot(spec, day, sess, physician, contact, qual=None):
            return MasterSlot(
                hospital_id=mgh.id,
                day_of_week=day,
                specialty=spec,
                physician=physician,
                time_block=sess,
                contact_email=contact,
                session=sess,
                qualifier=qual,
            )

        stroke_email = "avc.hgm@muhc.mcgill.ca"
        gen_email = "mara.divittori@muhc.mcgill.ca"
        mvmt_email = "silvana.dilollo@muhc.mcgill.ca"

        slots = [
            # STROKE
            slot("STROKE", "Monday", "AM", "Dr. Ehrensperger", stroke_email),
            slot("STROKE", "Monday", "AM", "Dr. Legault", stroke_email),
            slot("STROKE", "Tuesday", "AM", "Dr. Ehrensperger", stroke_email),
            slot("STROKE", "Wednesday", "AM", "Dr. Durcan", stroke_email, qual="wk 1&3"),
            slot("STROKE", "Wednesday", "AM", "Dr. Legault", stroke_email),
            slot("STROKE", "Thursday", "AM", "Dr. Minuk", stroke_email),
            slot("STROKE", "Thursday", "AM", "Dr. Ehrensperger", stroke_email),
            slot("STROKE", "Thursday", "AM", "Dr. Legault", stroke_email),
            slot("STROKE", "Thursday", "AM", "Dr. Moussaddy", stroke_email),
            slot("STROKE", "Friday", "AM", "Dr. Ehrensperger", stroke_email),
            slot("STROKE", "Friday", "AM", "Dr. Wein", stroke_email),
            slot("STROKE", "Monday", "PM", "Dr. Ehrensperger", stroke_email),
            slot("STROKE", "Monday", "PM", "Dr. Legault", stroke_email),
            slot("STROKE", "Tuesday", "PM", "Dr. Ehrensperger", stroke_email),
            slot("STROKE", "Wednesday", "PM", "Dr. Durcan", stroke_email, qual="wk 1&3"),
            slot("STROKE", "Wednesday", "PM", "Dr. Legault", stroke_email),
            slot("STROKE", "Thursday", "PM", "Dr. Ehrensperger", stroke_email),
            slot("STROKE", "Thursday", "PM", "Dr. Legault", stroke_email),
            slot("STROKE", "Thursday", "PM", "Dr. Moussaddy", stroke_email),
            # GENERAL NEURO
            slot("GENERAL NEURO", "Monday", "AM", "Dr. Chalk", gen_email),
            slot("GENERAL NEURO", "Tuesday", "AM", "Dr. Chalk", gen_email),
            slot("GENERAL NEURO", "Wednesday", "AM", "Dr. Ehrensperger", gen_email),
            slot("GENERAL NEURO", "Monday", "PM", "Dr. Lubarsky", gen_email, qual="12–4"),
            slot("GENERAL NEURO", "Wednesday", "PM", "Dr. Ehrensperger", gen_email),
            slot("GENERAL NEURO", "Thursday", "PM", "Dr. Lubarsky", gen_email, qual="12–4"),
            # MOVEMENT DISORDER
            slot("MOVEMENT DISORDER", "Monday", "AM", "Dr. Lafontaine", mvmt_email, qual="9–12"),
            slot("MOVEMENT DISORDER", "Tuesday", "AM", "Dr. Lafontaine", mvmt_email, qual="9–12"),
            slot("MOVEMENT DISORDER", "Tuesday", "AM", "Dr. Huot", mvmt_email, qual="9–12"),
            slot("MOVEMENT DISORDER", "Monday", "PM", "Dr. Postuma", mvmt_email, qual="1–4:30"),
            slot("MOVEMENT DISORDER", "Monday", "PM", "Dr. Rabinovitch", mvmt_email, qual="1–4:30"),
            slot("MOVEMENT DISORDER", "Tuesday", "PM", "Dr. Lafontaine", mvmt_email, qual="1–4:00"),
            slot("MOVEMENT DISORDER", "Tuesday", "PM", "Dr. Huot", mvmt_email, qual="1–4:00"),
            slot("MOVEMENT DISORDER", "Thursday", "PM", "Dr. Postuma", mvmt_email, qual="1–4:30"),
            # MYASTHENIA GRAVIS
            slot("MYASTHENIA GRAVIS", "Friday", "AM", "Dr. Chalk", gen_email),
            # NEUROPATHY
            slot("NEUROPATHY", "Tuesday", "PM", "Dr. Chalk", gen_email),
            # URGENT NEURO
            slot("URGENT NEURO", "Monday", "PM", "Dr. Lubarsky", gen_email, qual="12–4"),
            slot("URGENT NEURO", "Thursday", "PM", "Dr. Lubarsky", gen_email, qual="12–4"),
            # VESTIBULAR
            slot("VESTIBULAR", "Monday", "AM", "Dr. Choi", gen_email, qual="TBC"),
            slot("VESTIBULAR", "Tuesday", "AM", "Dr. Choi", gen_email, qual="TBC"),
            slot("VESTIBULAR", "Wednesday", "AM", "Dr. Choi", gen_email, qual="TBC"),
            slot("VESTIBULAR", "Thursday", "AM", "Dr. Choi", gen_email, qual="TBC"),
            slot("VESTIBULAR", "Friday", "AM", "Dr. Choi", gen_email, qual="TBC"),
            slot("VESTIBULAR", "Monday", "PM", "Dr. Choi", gen_email, qual="TBC"),
            slot("VESTIBULAR", "Tuesday", "PM", "Dr. Choi", gen_email, qual="TBC"),
            slot("VESTIBULAR", "Wednesday", "PM", "Dr. Choi", gen_email, qual="TBC"),
            slot("VESTIBULAR", "Thursday", "PM", "Dr. Choi", gen_email, qual="TBC"),
            slot("VESTIBULAR", "Friday", "PM", "Dr. Choi", gen_email, qual="TBC"),
        ]
        session.add_all(slots)
        session.commit()

        print("🌱 Seeding MNH Master Schedule...")

        def mnh_rows(spec, day, physician, time_str, contact, qual=None):
            """Expand 'AM/PM' into two session rows; otherwise a single row.
            time_str defaults to 'AM/PM' when blank."""
            t = (time_str or "AM/PM").strip()
            block = t if t in ("AM", "PM", "AM/PM") else "AM/PM"
            sessions = ["AM", "PM"] if block == "AM/PM" else [block]
            return [
                MasterSlot(
                    hospital_id=mnh.id,
                    day_of_week=day,
                    specialty=spec,
                    physician=physician,
                    time_block=block,
                    contact_email=contact,
                    session=s,
                    qualifier=qual,
                )
                for s in sessions
            ]

        epilepsy_jg = "julie.gascon@muhc.mcgill.ca"
        epilepsy_rv = "roula.vrentzos@muhc.mcgill.ca"
        psych_email = "beatrice.stoklas@muhc.mcgill.ca"
        als_email = "ritsa.argyriou@muhc.mcgill.ca"
        nm_email = "erin.oferrall@mcgill.ca"
        emg_email = "marcella.bolfa@muhc.mcgill.ca"
        ms_email = "mariaangela.costa@muhc.mcgill.ca"
        cog_email = "emma.damrie.comtl@ssss.gouv.qc.ca"
        gen_neuro_email = "jocelyn.bigot@muhc.mcgill.ca"
        mvmt_mnh_email = "stefania.ianni@muhc.mcgill.ca"

        mnh_specs: list[MasterSlot] = []

        # ----- Monday -----
        mnh_specs += mnh_rows("EPILEPSY", "Monday", "Dr. Dubeau", "AM/PM", epilepsy_jg)
        mnh_specs += mnh_rows("EPILEPSY", "Monday", "Dr. Pana", "AM/PM", epilepsy_jg)
        mnh_specs += mnh_rows("EPILEPSY", "Monday", "Dr. Veilleux", "AM/PM", epilepsy_rv)
        mnh_specs += mnh_rows("PSYCHIATRY", "Monday", "Dr. Trounce", "AM/PM", psych_email)
        mnh_specs += mnh_rows("NEUROPSYCHIATRY", "Monday", "Dr. Kolivakis", "PM", psych_email)
        mnh_specs += mnh_rows("NEUROCOGNITIVE", "Monday", "Dr. de Villers-Sidani", "AM", psych_email)
        mnh_specs += mnh_rows("ALS", "Monday", "Dr. Massie", "AM/PM", als_email)
        mnh_specs += mnh_rows("NEUROMUSCULAR", "Monday", "Dr. Blanchard", "", nm_email)
        mnh_specs += mnh_rows("EMG", "Monday", "EMG Lab", "AM/PM", emg_email)

        # ----- Tuesday -----
        mnh_specs += mnh_rows("EPILEPSY", "Tuesday", "Dr. Dubeau", "AM", epilepsy_jg)
        mnh_specs += mnh_rows("EPILEPSY", "Tuesday", "Dr. Pana", "AM/PM", epilepsy_jg)
        mnh_specs += mnh_rows("EPILEPSY", "Tuesday", "Dr. Di Battista", "AM/PM", epilepsy_jg, qual="once a month")
        mnh_specs += mnh_rows("EPILEPSY", "Tuesday", "Dr. Veilleux", "AM/PM", epilepsy_rv)
        mnh_specs += mnh_rows("EPILEPSY", "Tuesday", "Dr. Dubeau", "PM", epilepsy_rv)
        mnh_specs += mnh_rows("NEUROINFLAMMATORY", "Tuesday", "Dr. Harroud", "", ms_email)
        mnh_specs += mnh_rows("NEUROINFLAMMATORY", "Tuesday", "Dr. Thebault", "", ms_email)
        mnh_specs += mnh_rows("NEUROINFLAMMATORY", "Tuesday", "Dr. Nobile", "", ms_email)
        mnh_specs += mnh_rows("NEUROPSYCHIATRY", "Tuesday", "Dr. Benrimoh", "PM", epilepsy_rv)
        mnh_specs += mnh_rows("NEUROPSYCHIATRY", "Tuesday", "Dr. Gobbi", "AM/PM", epilepsy_rv)
        mnh_specs += mnh_rows("NEUROCOGNITIVE", "Tuesday", "Dr. Maiya Geddes", "AM", cog_email)
        mnh_specs += mnh_rows("NEUROGENETICS", "Tuesday", "Dr. Srour", "AM/PM", epilepsy_rv)

        # ----- Wednesday -----
        mnh_specs += mnh_rows("NEUROMUSCULAR", "Wednesday", "Dr. O'Ferral", "AM/PM", nm_email)
        mnh_specs += mnh_rows("NEUROMUSCULAR", "Wednesday", "Dr. Blanchard", "AM/PM", nm_email)
        mnh_specs += mnh_rows("NEUROMUSCULAR", "Wednesday", "Dr. Massie", "AM/PM", nm_email)
        mnh_specs += mnh_rows("EPILEPSY", "Wednesday", "Dr. Veilleux", "AM/PM", epilepsy_rv, qual="Telemed only")

        # ----- Thursday -----
        mnh_specs += mnh_rows("EPILEPSY", "Thursday", "Dr. Dubeau", "AM/PM", epilepsy_jg)
        mnh_specs += mnh_rows("GENERAL NEURO", "Thursday", "Dr. Durcan", "", gen_neuro_email)
        mnh_specs += mnh_rows("NEUROCOGNITIVE", "Thursday", "Dr. de Villers-Sidani", "AM/PM", psych_email)
        mnh_specs += mnh_rows("NEUROCOGNITIVE", "Thursday", "Dr. Fellows", "AM", psych_email)
        mnh_specs += mnh_rows("ALS", "Thursday", "ALS Team", "AM/PM", als_email)
        mnh_specs += mnh_rows("NEUROINFLAMMATORY", "Thursday", "Dr. Giacomini", "AM/PM", ms_email)
        mnh_specs += mnh_rows("NEUROINFLAMMATORY", "Thursday", "Dr. Saveriano", "AM/PM", ms_email)

        # ----- Friday -----
        for phys in ("Dr. Fon", "Dr. Lafontaine", "Dr. Postuma", "Dr. Sharp"):
            mnh_specs += mnh_rows("MOVEMENT DISORDER", "Friday", phys, "AM/PM", mvmt_mnh_email)
        mnh_specs += mnh_rows("MOVEMENT DISORDER", "Friday", "Dr. Dagher", "AM", mvmt_mnh_email)
        mnh_specs += mnh_rows("MOVEMENT DISORDER", "Friday", "Dr. Rouleau", "AM", mvmt_mnh_email)
        mnh_specs += mnh_rows("NEUROMUSCULAR", "Friday", "Dr. O'Ferral", "AM", nm_email)
        mnh_specs += mnh_rows("NEUROMUSCULAR", "Friday", "Dr. Massie", "AM", nm_email)
        mnh_specs += mnh_rows("PHYSIATRY", "Friday", "Dr. Daria Trojan", "AM/PM", psych_email)

        session.add_all(mnh_specs)
        session.commit()

        print("🌱 Seeding Resident's Personal Bookings...")
        booking_1 = BookedSlot(
            user_id=resident_1.id,
            hospital_name=mgh.name,
            physician="Dr. Ehrensperger",
            specialty="STROKE",
            time_block="AM",
            contact_email=stroke_email,
            status=SlotStatus.to_contact,
            date=date.today(),
        )
        booking_2 = BookedSlot(
            user_id=resident_1.id,
            hospital_name=mgh.name,
            physician="Dr. Postuma",
            specialty="MOVEMENT DISORDER",
            time_block="PM",
            contact_email=mvmt_email,
            status=SlotStatus.emailed,
            date=date(2026, 6, 21),
            notes="Sent email asking for shadowing availability.",
        )
        booking_custom = BookedSlot(
            user_id=resident_1.id,
            hospital_name=mnh.name,
            physician="Dr. Custom",
            specialty="External Clinic Sync",
            time_block="AM",
            contact_email="custom@mcgill.ca",
            status=SlotStatus.confirmed,
            date=date(2026, 6, 22),
            notes="Approved by Dr. Allen.",
        )

        session.add_all([booking_1, booking_2, booking_custom])
        session.commit()

        print("\n🎉 Database successfully seeded with test data!")


if __name__ == "__main__":
    seed_data()
