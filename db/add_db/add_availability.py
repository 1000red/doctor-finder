"""
Seed script to populate doctor_availability with time slots
for each doctor over the next N days.

Safe to re-run: skips (doctor_id, date, start_time, end_time)
combinations that already exist.

Run with: python -m db.add_db.add_availability
"""

import random
from datetime import date, datetime, timedelta

from db.database import SessionLocal
from models.doctor import Doctor
from models.doctor_availability import DoctorAvailability

DAYS_AHEAD = 14
SLOT_DURATION_MINUTES = 30
WORK_START_HOUR = 9
WORK_END_HOUR = 17
CHANCE_DAY_OFF = 0.15  # احتمال إن اليوم يبقى إجازة للدكتور


def generate_time_slots() -> list[tuple[str, str]]:
    slots = []
    current = datetime.combine(date.today(), datetime.min.time()).replace(hour=WORK_START_HOUR)
    end_of_day = current.replace(hour=WORK_END_HOUR)

    while current < end_of_day:
        slot_end = current + timedelta(minutes=SLOT_DURATION_MINUTES)
        slots.append((current.strftime("%H:%M"), slot_end.strftime("%H:%M")))
        current = slot_end

    return slots


def seed_availability():
    db = SessionLocal()
    try:
        doctors = db.query(Doctor).all()
        if not doctors:
            print("No doctors found in the database. Please seed doctors first.")
            return

        time_slots = generate_time_slots()
        today = date.today()
        total_added = 0
        total_skipped = 0

        for doctor in doctors:
            for day_offset in range(DAYS_AHEAD):
                current_date = today + timedelta(days=day_offset)

                if random.random() < CHANCE_DAY_OFF:
                    continue  # يوم إجازة للدكتور

                existing_slots = {
                    (a.start_time, a.end_time)
                    for a in db.query(DoctorAvailability)
                    .filter(
                        DoctorAvailability.doctor_id == doctor.doctor_id,
                        DoctorAvailability.date == current_date,
                    )
                    .all()
                }

                for start_time, end_time in time_slots:
                    if (start_time, end_time) in existing_slots:
                        total_skipped += 1
                        continue

                    slot = DoctorAvailability(
                        doctor_id=doctor.doctor_id,
                        date=current_date,
                        start_time=start_time,
                        end_time=end_time,
                        is_available=True,
                    )
                    db.add(slot)
                    total_added += 1

            db.flush()
            print(f"Doctor {doctor.doctor_id} ({doctor.name}): slots generated")

        db.commit()
        print(f"\nDone. Total slots added: {total_added}, skipped (already existed): {total_skipped}")

    except Exception as e:
        db.rollback()
        print(f"Error while seeding availability: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_availability()