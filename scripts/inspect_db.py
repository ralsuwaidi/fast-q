from seed import BookedSlot, Hospital, MasterSlot, User
from sqlmodel import Session, create_engine, select

engine = create_engine("sqlite:///database.db")

def inspect():
    with Session(engine) as session:
        print("\n--- 🏥 HOSPITALS ---")
        hospitals = session.exec(select(Hospital)).all()
        for h in hospitals:
            print(f"[{h.id}] {h.name}")

        print("\n--- 🧑‍⚕️ USERS ---")
        users = session.exec(select(User)).all()
        for u in users:
            print(f"[{u.id}] {u.full_name} ({u.email}) - Role: {u.role}")

        print("\n--- 📅 MASTER SCHEDULE ---")
        slots = session.exec(select(MasterSlot)).all()
        for s in slots:
            print(f"[{s.id}] {s.day_of_week}: {s.specialty} with {s.physician} ({s.time_block})")

        print("\n--- 📌 RESIDENT BOOKINGS ---")
        bookings = session.exec(select(BookedSlot)).all()
        for b in bookings:
            if b.master_slot_id:
                print(f"[{b.id}] User {b.user_id} booked MasterSlot {b.master_slot_id} -> Status: {b.status}")
            else:
                print(f"[{b.id}] User {b.user_id} custom shift: {b.custom_title} -> Status: {b.status}")
        print("\n")

if __name__ == "__main__":
    inspect()