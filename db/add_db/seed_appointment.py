"""
Seed script to populate doctor_availability with time slots from each
doctor's recurring weekly working-hours schedule.

Safe to re-run: skips (doctor_id, date, start_time, end_time)
combinations that already exist.

Run with: python3 -m db.add_db.add_appointment
"""

from datetime import date, datetime, timedelta

from db.database import SessionLocal
from models.doctor import Doctor
from models.doctor_availability import DoctorAvailability
from models.doctor_working_hours import DoctorWorkingHours

DAYS_AHEAD = 14
SLOT_DURATION_MINUTES = 30


def generate_time_slots(start_time: str, end_time: str) -> list[tuple[str, str]]:
    slots = []
    current = datetime.strptime(start_time, "%H:%M")
    end_of_day = datetime.strptime(end_time, "%H:%M")

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

        today = date.today()
        total_added = 0
        total_skipped = 0

        for doctor in doctors:
            working_hours_by_day = {
                hours.day_of_week: hours
                for hours in db.query(DoctorWorkingHours)
                .filter(DoctorWorkingHours.doctor_id == doctor.doctor_id)
                .all()
            }

            if not working_hours_by_day:
                print(f"Doctor {doctor.doctor_id} ({doctor.name}): no working hours configured, skipped")
                continue

            for day_offset in range(DAYS_AHEAD):
                current_date = today + timedelta(days=day_offset)
                working_hours = working_hours_by_day.get(current_date.weekday())
                if not working_hours:
                    continue

                time_slots = generate_time_slots(
                    working_hours.start_time,
                    working_hours.end_time,
                )

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
