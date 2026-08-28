"""Add a default weekly schedule for doctors without working hours.

Existing schedules are never changed, so this is safe to run more than once.

Run with: python3 -m db.add_db.add_working_hours
"""

from db.database import SessionLocal
from models.doctor import Doctor
from models.doctor_working_hours import DoctorWorkingHours

DEFAULT_START_TIME = "09:00"
DEFAULT_END_TIME = "17:00"
DAYS_OF_WEEK = range(7)  # Monday (0) through Sunday (6)


def seed_missing_working_hours() -> None:
    db = SessionLocal()
    try:
        doctors = db.query(Doctor).all()
        total_doctors_updated = 0
        total_rows_added = 0

        for doctor in doctors:
            configured_days = {
                row.day_of_week
                for row in db.query(DoctorWorkingHours.day_of_week)
                .filter(DoctorWorkingHours.doctor_id == doctor.doctor_id)
                .all()
            }
            # A doctor with any configured day may intentionally be off on the
            # remaining days, so never fill a partial schedule automatically.
            if configured_days:
                continue

            db.add_all(
                [
                    DoctorWorkingHours(
                        doctor_id=doctor.doctor_id,
                        day_of_week=day_of_week,
                        start_time=DEFAULT_START_TIME,
                        end_time=DEFAULT_END_TIME,
                    )
                    for day_of_week in DAYS_OF_WEEK
                ]
            )
            total_doctors_updated += 1
            total_rows_added += len(DAYS_OF_WEEK)

        db.commit()
        print(
            f"Done. Added {total_rows_added} working-hours rows "
            f"for {total_doctors_updated} doctors."
        )
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_missing_working_hours()
