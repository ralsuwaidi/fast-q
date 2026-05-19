import os
import sys
from pathlib import Path

from sqlmodel import Session, select

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
os.environ.setdefault("PYTHONPATH", "src")

from core.database import engine  # noqa: E402
from seed import BookedSlot, Hospital, MasterSlot, User  # noqa: E402


def inspect():
    with Session(engine) as session:
        print("\n--- HOSPITALS ---")
        for h in session.exec(select(Hospital)).all():
            print(f"[{h.id}] {h.name}")

        print("\n--- USERS ---")
        for u in session.exec(select(User)).all():
            print(f"[{u.id}] {u.full_name} ({u.email}) - Role: {u.role}")

        print("\n--- MASTER SCHEDULE ---")
        for s in session.exec(select(MasterSlot)).all():
            print(f"[{s.id}] {s.day_of_week}: {s.specialty} with {s.physician} ({s.time_block})")

        print("\n--- RESIDENT BOOKINGS ---")
        for b in session.exec(select(BookedSlot)).all():
            print(f"[{b.id}] User {b.user_id} {b.physician} on {b.date} ({b.time_block}) -> {b.status}")
        print()


if __name__ == "__main__":
    inspect()
